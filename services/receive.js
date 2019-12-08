/**
 * Copyright 2019-present, Facebook, Inc. All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 *
 * Messenger For Original Coast Clothing
 * https://developers.facebook.com/docs/messenger-platform/getting-started/sample-apps/original-coast-clothing
 */

"use strict";

const Response = require("./response"),
  GraphAPi = require("./graph-api"),
  request = require("request"),
  i18n = require("../i18n.config");

module.exports = class Receive {
  constructor(user, webhookEvent) {
    this.user = user;
    this.webhookEvent = webhookEvent;
  }

  // Check if the event is a message or postback and
  // call the appropriate handler function
  handleMessage() {
    let event = this.webhookEvent;

    let responses;

    try {
      if (event.message) {
        let message = event.message;

        if (message.attachments) {
          responses = this.handleAttachmentMessage();
        } else if (message.text) {
          responses = this.handleTextMessage();
        }
      }
    } catch (error) {
      console.error(error);
      responses = {
        text: `An error has occured: '${error}'. We have been notified and \
        will fix the issue shortly!`
      };
    }

    if (Array.isArray(responses)) {
      let delay = 0;
      for (let response of responses) {
        this.sendMessage(response, delay * 2000);
        delay++;
      }
    } else {
      this.sendMessage(responses);
    }
  }

  // Handles messages events with text
  handleTextMessage() {
    console.log(
      "Received text:",
      `${this.webhookEvent.message.text} for ${this.user.psid}`
    );

    // check greeting is here and is confident
    let greeting = this.firstEntity(this.webhookEvent.message.nlp, "greetings");

    let message = this.webhookEvent.message.text.trim().toLowerCase();

    let response;

    if (
      (greeting && greeting.confidence > 0.8) ||
      message.includes("start over")
    ) {
      response = Response.genNuxMessage(this.user);
    } else {
      response = [Response.genText(i18n.__("get_started.guidance"))];
    }

    return response;
  }

  // Handles mesage events with attachments
  async handleAttachmentMessage() {
    let response;

    // let lookalike;

    // Get the attachment
    let attachment = this.webhookEvent.message.attachments[0];
    console.log("Received attachment:", `${attachment} for ${this.user.psid}`);

    const imgUrl = attachment.payload.url;
    console.log(imgUrl);

    const lookalike = await request.post(
      // Change this to localhost
      "http://127.0.0.1:5000/predict",
      {
        json: {
          imgUrl: imgUrl
        }
      },
      async (error, res, body) => {
        if (error) {
          console.error(error);
          return;
        }
        console.log(`statusCode: ${res.statusCode}`);
        console.log(body);

        console.log("body.lookalike: ", body.lookalike);
        // lookalike = body.lookalike;
        return await body.lookalike;
      }
    );

    console.log("Lookalike: ", lookalike);

    response = Response.genText(
      "Our advanced CNNs and ML and AI say you look like: ",
      lookalike
    );

    return response;
  }

  // handlePrivateReply(type, object_id) {
  //   let welcomeMessage =
  //     i18n.__("get_started.welcome") +
  //     " " +
  //     i18n.__("get_started.guidance") +
  //     ". " +
  //     i18n.__("get_started.help");

  //   let response = Response.genQuickReply(welcomeMessage, [
  //     {
  //       title: i18n.__("menu.suggestion"),
  //       payload: "CURATION"
  //     },
  //     {
  //       title: i18n.__("menu.help"),
  //       payload: "CARE_HELP"
  //     }
  //   ]);

  //   let requestBody = {
  //     recipient: {
  //       [type]: object_id
  //     },
  //     message: response
  //   };

  //   GraphAPi.callSendAPI(requestBody);
  // }

  sendMessage(response, delay = 0) {
    // Check if there is delay in the response
    if ("delay" in response) {
      delay = response["delay"];
      delete response["delay"];
    }

    // Construct the message body
    let requestBody = {
      recipient: {
        id: this.user.psid
      },
      message: response
    };

    // // Check if there is persona id in the response
    // if ("persona_id" in response) {
    //   let persona_id = response["persona_id"];
    //   delete response["persona_id"];

    //   requestBody = {
    //     recipient: {
    //       id: this.user.psid
    //     },
    //     message: response,
    //     persona_id: persona_id
    //   };
    // }

    setTimeout(() => GraphAPi.callSendAPI(requestBody), delay);
  }

  firstEntity(nlp, name) {
    return nlp && nlp.entities && nlp.entities[name] && nlp.entities[name][0];
  }
};
