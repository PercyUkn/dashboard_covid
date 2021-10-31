 window.watsonAssistantChatOptions = {
      integrationID: "c954a396-4404-43ec-b5bf-4eb7ea423f3b", // The ID of this integration.
      region: "us-south", // The region your integration is hosted in.
      serviceInstanceID: "4b9d6014-8a53-4236-8fee-68c345834441", // The ID of your service instance.
      onLoad: function(instance) { instance.render(); }
    };
  setTimeout(function(){
    const t=document.createElement('script');
    t.src="https://web-chat.global.assistant.watson.appdomain.cloud/versions/" + (window.watsonAssistantChatOptions.clientVersion || 'latest') + "/WatsonAssistantChatEntry.js"
    document.head.appendChild(t);
  });