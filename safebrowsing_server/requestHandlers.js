
var handles = {};
handles["/list"] = handle_list_request;
handles["/downloads"] = handle_download_request;

var fs = require('fs');

/* handle request for available lists */
function handle_list_request(context, response, callback)
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
function handle_download_request(context, response, callback)
{
  if (typeof context.data != 'undefined')
    console.log(">>>" + context.data + "<<<");

  var req_listname = "mozpub-track-digest256";
  var req_chunknum;

  if (typeof context.data != 'undefined')
  {
    var data = context.data.split("\n");
    if (data.length > 0)
    {
      var line_leftright = data[0].split(";");
      if (line_leftright.length > 0)
        req_listname = line_leftright[0];
      if (line_leftright.length > 1)
        req_chunknum = line_leftright[1];
    }
  }

  /* 60 minutes polling time, list name is mozpub-track-digest256 */
  var data_header = "n:60\ni:" + req_listname + "\n";
  /* reset header to flush all old entries */
  var reset_header = "n:60\nr:pleasereset\n";

  fs.readFile(req_listname, function(err, data)
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
      /* get string prefix of data */
      var data_s = "";
      for (var d = 0; d < data.length; d++)
      {
        if (data[d] == 0x0a) // '\n'
          break;
        data_s += data.toString('utf-8', d, d + 1);
      }

      /* no specific chunk was requested. return all. */
      if (typeof req_chunknum == 'undefined' || req_chunknum == "")
      {
        /* 
         * since we are returning a mix of ASCII and binary data 
         * we need to cast the ASCII data into a raw buffer and 
         * concatenate it with the binary data to preserve their 
         * raw nature. 
         * */
        var buffer = new Buffer(data_header, "binary");
        buffer = Buffer.concat([buffer, data])

        console.log("[#] returning all data " + buffer.length + " bytes");

        callback(response, {
          'statusCode': 200, 
          'responseHeaders': {'Content-Type': 'application/octet-stream'}, 
          'responseBody': buffer
        });
      }
      /* client already has everything (req_chunknum is what we're serving) */
      else if (data_s.indexOf(req_chunknum + ":") == 0)
      {
        console.log("[#] returning no new data");

        callback(response, {
          'statusCode': 200, 
          'responseHeaders': {'Content-Type': 'text/plain'}, 
          'responseBody': data_header
        });
      }
      /* client has requested a different chunk than the current one */
      else
      {
        console.log("[#] returning reset directive");

        callback(response, {
          'statusCode': 200, 
          'responseHeaders': {'Content-Type': 'text/plain'}, 
          'responseBody': reset_header
        });
      }
    }
  });
}

/* determine which handler to call */
function route(context, response, callback)
{
  if (typeof handles[context.path] == 'function')
  {
    console.log("[#] handling " + context.path);

    handles[context.path](context, response, callback);
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
