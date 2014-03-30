var server = require("./server");
var router = require("./router");
var requestHandlers = require("./requestHandlers");

var handle = {};
handle["/list"] = requestHandlers.list;
handle["/info"] = requestHandlers.info;
handle["/mix"] = requestHandlers.mix;

server.start(router.route, handle);
