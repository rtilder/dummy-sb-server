
// basic http module
var http = require("http");

// url parsing
var url = require("url");

// http.server instance
var server;

// function routing requests
var route;

function printClientInfo(request)
{
  var client;

  client = request.socket.address();

  console.log("\n* Connection from " + client.address + " port " + client.port);

  console.log("> " + request.method + " " + request.url 
    + " HTTP/" + request.httpVersion);

  for (var header in request.headers)
    console.log("> " + header + ": " + request.headers[header]);

  console.log(">");
}

function processRequest(request)
{
  // parse the URL, extract path
  var urlObj = url.parse(request.url);

  // TODO: extract query

  return {'path': urlObj.pathname};
}

function onRequest(request, response)
{
  var responseBlob;

  // print stuff about the client and its request
  printClientInfo(request);

  // TODO: on 'data', read POST request body

  // pass processed request to route function. 
  // reponse callback will be used by route function 
  // to return content when ready
  route(processRequest(request), response, function(response, responseBlob) 
  {
    try {
     response.writeHead(responseBlob.statusCode, responseBlob.responseHeaders);
     response.write(responseBlob.responseBody);
     response.end();
    }
    catch (e)
    {
      // Internal server error
      response.writeHead(500);
      response.end();
    }
  });
}

function onListen()
{
  var listeningAddress = server.address();

  console.log("[-] Server is up and listening at " 
    + listeningAddress.address + ":" + listeningAddress.port);
}

function start(_route)
{
  // create an http server instance
  server = http.createServer(onRequest);

  // initialize route function pointer
  route = _route;

  // bring http server up
  server.listen(80, onListen);
}

exports.start = start;
