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

// const Curation = require("./curation"),
// Order = require("./order"),
const Response = require("./response"),
  // Care = require("./care"),
  // Survey = require("./survey"),
  GraphAPi = require("./graph-api"),
  fs = require("fs"),
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

        // if (message.quick_reply) {
        //   responses = this.handleQuickReply();
        // } else
        if (message.attachments) {
          responses = this.handleAttachmentMessage();
        } else if (message.text) {
          responses = this.handleTextMessage();
        }
      }
      // else if (event.postback) {
      //   responses = this.handlePostback();
      // } else if (event.referral) {
      //   responses = this.handleReferral();
      // }
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

    // const response = Response.genText(
    //   "Sorry but we don't yet support text messaging. Please send a picture instead."
    // );

    if (
      (greeting && greeting.confidence > 0.8) ||
      message.includes("start over")
    ) {
      response = Response.genNuxMessage(this.user);
    }
    // else if (Number(message)) {
    //   response = Order.handlePayload("ORDER_NUMBER");
    // } else if (message.includes("#")) {
    //   response = Survey.handlePayload("CSAT_SUGGESTION");
    // } else if (message.includes(i18n.__("care.help").toLowerCase())) {
    //   let care = new Care(this.user, this.webhookEvent);
    //   response = care.handlePayload("CARE_HELP");
    // }
    else {
      response = [
        Response.genText(
          i18n.__("fallback.any", {
            message: this.webhookEvent.message.text
          })
        ),
        Response.genText(i18n.__("get_started.guidance"))
        // Response.genQuickReply(i18n.__("get_started.help"), [
        //   {
        //     title: i18n.__("menu.suggestion"),
        //     payload: "CURATION"
        //   },
        //   {
        //     title: i18n.__("menu.help"),
        //     payload: "CARE_HELP"
        //   }
        // ])
      ];
    }

    return response;
  }

  // Handles mesage events with attachments
  handleAttachmentMessage() {
    // TODO: Here run the picture through the model

    let response;

    // Get the attachment
    let attachment = this.webhookEvent.message.attachments[0];
    console.log("Received attachment:", `${attachment} for ${this.user.psid}`);

    // console.log(fs.readFileSync(attachment).buffer.toString("base64"));
    // console.log(Buffer.from(attachment).toString("base64"));

    // function to encode file data to base64 encoded string
    function base64_encode(file) {
      // read binary data
      const bitmap = fs.readFileSync(file);
      // convert binary data to base64 encoded string
      return new Buffer(bitmap).toString("base64");
    }

    // convert image to base64 encoded string
    const base64str = base64_encode(attachment);
    console.log(base64str);

    response = Response.genText(
      "Thanks for sending this picture!!! I'm just analysing it now."
    );

    // TODO: Convert image to base64
    // TODO: Post base64 to Flask server
    // TODO: Listen for response from Flask server

    //  Listen for post/get requests (app.js)
    request.post(
      // Change this to localhost
      "http://127.0.0.1:5000/predict",
      {
        json: {
          imgString: "base64 image"
        }
      },
      (error, res, body) => {
        if (error) {
          console.error(error);
          return;
        }
        console.log(`statusCode: ${res.statusCode}`);
        console.log(body);
      }
    );

    return response;
  }

  // // Handles mesage events with quick replies
  // handleQuickReply() {
  //   // Get the payload of the quick reply
  //   let payload = this.webhookEvent.message.quick_reply.payload;

  //   return this.handlePayload(payload);
  // }

  // // Handles postbacks events
  // handlePostback() {
  //   let postback = this.webhookEvent.postback;
  //   // Check for the special Get Starded with referral
  //   let payload;
  //   if (postback.referral && postback.referral.type == "OPEN_THREAD") {
  //     payload = postback.referral.ref;
  //   } else {
  //     // Get the payload of the postback
  //     payload = postback.payload;
  //   }
  //   return this.handlePayload(payload.toUpperCase());
  // }

  // // Handles referral events
  // handleReferral() {
  //   // Get the payload of the postback
  //   let payload = this.webhookEvent.referral.ref.toUpperCase();

  //   return this.handlePayload(payload);
  // }

  // handlePayload(payload) {
  //   console.log("Received Payload:", `${payload} for ${this.user.psid}`);

  //   // Log CTA event in FBA
  //   GraphAPi.callFBAEventsAPI(this.user.psid, payload);

  //   let response;

  //   // Set the response based on the payload
  //   if (
  //     payload === "GET_STARTED" ||
  //     payload === "DEVDOCS" ||
  //     payload === "GITHUB"
  //   ) {
  //     response = Response.genNuxMessage(this.user);
  //   } else if (payload.includes("CURATION") || payload.includes("COUPON")) {
  //     let curation = new Curation(this.user, this.webhookEvent);
  //     response = curation.handlePayload(payload);
  //   } else if (payload.includes("CARE")) {
  //     let care = new Care(this.user, this.webhookEvent);
  //     response = care.handlePayload(payload);
  //   } else if (payload.includes("ORDER")) {
  //     response = Order.handlePayload(payload);
  //   } else if (payload.includes("CSAT")) {
  //     response = Survey.handlePayload(payload);
  //   } else if (payload.includes("CHAT-PLUGIN")) {
  //     response = [
  //       Response.genText(i18n.__("chat_plugin.prompt")),
  //       Response.genText(i18n.__("get_started.guidance")),
  //       Response.genQuickReply(i18n.__("get_started.help"), [
  //         {
  //           title: i18n.__("care.order"),
  //           payload: "CARE_ORDER"
  //         },
  //         {
  //           title: i18n.__("care.billing"),
  //           payload: "CARE_BILLING"
  //         },
  //         {
  //           title: i18n.__("care.other"),
  //           payload: "CARE_OTHER"
  //         }
  //       ])
  //     ];
  //   } else {
  //     response = {
  //       text: `This is a default postback message for payload: ${payload}!`
  //     };
  //   }

  //   return response;
  // }

  handlePrivateReply(type, object_id) {
    let welcomeMessage =
      i18n.__("get_started.welcome") +
      " " +
      i18n.__("get_started.guidance") +
      ". " +
      i18n.__("get_started.help");

    let response = Response.genQuickReply(welcomeMessage, [
      {
        title: i18n.__("menu.suggestion"),
        payload: "CURATION"
      },
      {
        title: i18n.__("menu.help"),
        payload: "CARE_HELP"
      }
    ]);

    let requestBody = {
      recipient: {
        [type]: object_id
      },
      message: response
    };

    GraphAPi.callSendAPI(requestBody);
  }

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

    // Check if there is persona id in the response
    if ("persona_id" in response) {
      let persona_id = response["persona_id"];
      delete response["persona_id"];

      requestBody = {
        recipient: {
          id: this.user.psid
        },
        message: response,
        persona_id: persona_id
      };
    }

    setTimeout(() => GraphAPi.callSendAPI(requestBody), delay);
  }

  firstEntity(nlp, name) {
    return nlp && nlp.entities && nlp.entities[name] && nlp.entities[name][0];
  }
};
