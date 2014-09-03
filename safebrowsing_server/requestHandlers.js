
var handles = {};
handles["/list"] = handle_list_request;
handles["/downloads"] = handle_download_request;
handles["/update"] = handle_download_request;

/* 
 *  handle_download_request should only attempt to fetch these
 *  file names from the disk. Also used by handle_list_request
 *  to return available lists. Add more names here if more lists
 *  are to be served.
 *
 */
var valid_download_requests = [
"mozpub-track-digest256"
];

var fs = require('fs');

/* 
 * handle request for available lists 
 *
 * Browsers don't use this endpoint. They directly make specific requests 
 */
function handle_list_request(context, response, callback)
{
  var list = valid_download_requests.join("\n") + "\n";

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

  var req_listname = "";
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

  /*
   * make sure req_listname is found in valid_download_requests.
   * do not accept arbitrary file names here
   */
  if (valid_download_requests.indexOf(req_listname) == -1)
    req_listname="INVALID_LIST";

  /*
   * expand req_chunknum if necessary from range format
   * to explicit listing of chunk numbers
   */
  if (req_chunknum && req_chunknum != "" && req_chunknum.length > 2) {
    // copy command prefix to new req_chunknum
    new_req_chunknum = req_chunknum.substr(0,2);
    // strip command prefix from req_chunknum
    req_chunknum = req_chunknum.substr(2);
    // split req_chunknum into chunk number elements
    req_chunknum_elems = req_chunknum.split(",");
    // for each element do expand it if it describes a x-y range
    for (i = 0; i < req_chunknum_elems.length; i++) {
      req_chunknum_elem = req_chunknum_elems[i].split("-");
      // must expand a range
      if (req_chunknum_elem.length > 1) {
       for (j = parseInt(req_chunknum_elem[0]);
            j <= parseInt(req_chunknum_elem[1]); j++) {
         if (new_req_chunknum.length == 2)
           new_req_chunknum += j;
         else
           new_req_chunknum += "," + j;
         }
      }
      // no range to expand, just append as it is
      else {
        if (new_req_chunknum.length == 2)
          new_req_chunknum += req_chunknum_elem;
        else
          new_req_chunknum += "," + req_chunknum_elem;
      }
    }
    req_chunknum = new_req_chunknum;
  }

  /* 60 seconds polling time */
  /* TODO: change to 1800 or so for production */
  var data_header = "n:60\ni:" + req_listname + "\n";
  /* reset header to flush all old entries */
  /* TODO: change to 1800 or so for production */
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
      /*
       * get chunk numbers for this data and compare them
       * against req_chunknum that the client requested.
       */
      var chunks = "";
      var chunk_header = "";
      for (var d = 0; d < data.length; d++)
      {
        // extract chunk header, stops at a newline
        if (data[d] != 0x0a) // '\n'
          chunk_header += data.toString('utf-8', d, d + 1);
        else {
          // process chunk header
          var chunk_header_fields = chunk_header.split(":");
          var command  = chunk_header_fields[0];
          var chunknum = chunk_header_fields[1];
          var chunklen = chunk_header_fields[3];
          // add chunknum to chunks
          if (chunks == "")
            chunks = command + ":" + chunknum;
          else
            chunks += "," + chunknum;
          // advance chunklen bytes (skip over actual chunk data)
          // to reach potential next chunk header
          d += parseInt(chunklen);
          chunk_header = "";
        }
      }

      console.log("[#] chunks available: " + chunks);
      console.log("[#] chunks requested: " +
        (req_chunknum?req_chunknum:"NONE"));

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
      /* pretty rigid check right now */
      else if (chunks == req_chunknum)
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
        console.log("[#] returning reset directive. chunk: " + req_chunknum);

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
