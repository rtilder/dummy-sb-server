
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

  console.log("\n* " + (new Date)
    + " Connection from " + client.address
    + " port " + client.port);

  console.log("> " + request.method + " " + request.url
    + " HTTP/" + request.httpVersion);

  for (var header in request.headers)
    console.log("> " + header + ": " + request.headers[header]);

  console.log(">");
}

function parseCookies(cookies)
{
  var list = {},
  rc = cookies;

  rc && rc.split(';').forEach(function( cookie ) {
    var parts = cookie.split('=');
    list[parts.shift().trim()] = unescape(parts.join('='));
  });

  return list;
}

function processRequest(request, response)
{
  // parse the URL, extract path
  var urlObj = url.parse(request.url);

  // TODO: extract query string

  // parse request cookies
  var requestCookies =
    parseCookies(request.headers['cookie'] || "");

  // if debug_id cookie is found, do append it in responseHeaders (echo)
  if (typeof requestCookies['debug_id'] != 'undefined' &&
      requestCookies['debug_id'] != "") {
    response.responseHeaders =
      {'Set-Cookie': 'debug_id=' + requestCookies['debug_id']};
  }

  if (typeof request.requestData != 'undefined')
    return {'path': urlObj.pathname, 'data': request.requestData};
  else
    return {'path': urlObj.pathname};
}

function onRequest(request, response)
{
  var requestData = "";
  var responseBlob;

  // print stuff about the client and its request
  printClientInfo(request);

  if (request.method == 'POST')
  {
    request.on('data', function(chunk)
    {
      requestData += chunk.toString();
    });
    request.on('end', function()
    {
      request.requestData = requestData;

      route(processRequest(request, response), response, response_callback);
    });
  }
  else
  {
    // pass processed request to route function.
    // reponse callback will be used by route function
    // to return content when ready
    route(processRequest(request, response), response, response_callback);
  }
}

function response_callback(response, responseBlob)
{
  // generate a new debug_id cookie (48h) or use a pre-set Set-Cookie header
  responseBlob.responseHeaders['Set-Cookie'] =
    (response.responseHeaders && response.responseHeaders['Set-Cookie']) ||
    "debug_id=" + Math.floor(Math.random()*1000000000) + "; expires=" +
    new Date(new Date().getTime()+(60*60*48)*1000).toUTCString();

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
};

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

  // parse command-line options
  //
  // look for '--port' or '-p' in command-line arguments, fallback to 80
  var port = "";
  for (var i = 0; i < process.argv.length; i++) {
    if ((i + 1 < process.argv.length) &&
        (process.argv[i] == "--port" || process.argv[i] == "-p")) {
      port = parseInt(process.argv[i+1]);
      if (port > 0 && port < 65536) {
        console.log("[-] will listen on TCP " + port);
      }
      else {
        console.log("[-] invalid port number: " + port);
        port = "";
      }
    }
  }

  // defaults
  if (port == "") {
    port = 80;
    console.log("[-] will listen on TCP " + port
                + " (default). change that with '--port' or '-p'")
  }

  // bring http server up
  server.listen(port, onListen);
}

exports.start = start;
