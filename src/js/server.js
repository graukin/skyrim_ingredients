var http = require("http"),
    url = require("url");

function start(route, handle) {
  function onRequest(request, response) {
    console.log("Request on url: " + request.url);
    var parsed_url = url.parse(request.url, true);
    var path = parsed_url.pathname;
    var query = parsed_url.query;

    route(handle, path, query, response);
  }

  http.createServer(onRequest).listen(8888);
  console.log("Server started");
}

exports.start = start;
