
var handles = {};
handles["/list"] = handle_list_request;
handles["/downloads"] = handle_download_request;

var fs = require('fs');

/* handle request for available lists */
function handle_list_request(response, callback)
{
  var list = "mozpub-track-digest256\n";

  callback(response, {
    'statusCode': 200, 
    'responseHeaders': {'Content-Type': 'text/plain'}, 
    'responseBody': list
  });
}

/* 
 * handle request to download data from specific list(s). 
 * 
 * For now we ignore client's request body 
 * (list name(s) and report of existing chunks) 
 * and just serve mozpub-track-digest256 inline 
 * (no redirection used)
 */
function handle_download_request(response, callback)
{
  /* 60 minutes polling time, list name is mozpub-track-digest256 */
  var data_header = "n:60\ni:mozpub-track-digest256\n";

  fs.readFile('mozpub-track-digest256', function(err, data)
  {
    /* list file not found */
    if (err) 
    {
      console.log(err);

      callback(response, {
        'statusCode': 404, 
        'responseHeaders': {}, 'responseBody': ''});
    }
    else
    {
      /* 
       * since we are returning a mix of ASCII and binary data 
       * we need to cast the ASCII data into a raw buffer and 
       * concatenate it with the binary data to preserve their 
       * raw nature. 
       * */
      var buffer = new Buffer(data_header, "binary");
      buffer = Buffer.concat([buffer, data])

      callback(response, {
        'statusCode': 200, 
        'responseHeaders': {'Content-Type': 'application/octet-stream'}, 
        'responseBody': buffer
      });
    }
  });
}

/* determine which handler to call */
function route(context, response, callback)
{
  if (typeof handles[context.path] == 'function')
  {
    console.log("[#] handling " + context.path);

    handles[context.path](response, callback);
  }
  else
  {
    console.log("[!] No request handler found for " + context.path);

    callback(response, {
      'statusCode': 404, 'responseHeaders': {}, 'responseBody': ''
    });
  }
}

exports.route = route;
