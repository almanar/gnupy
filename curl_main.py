#
# Copyright Michael Groys, 2014
#
import optparse
import sys
import urllib2

postData = None
def dataOptCallback(option, opt, value, parser):
    global postData
    if len(value) > 0 and value[0] == '@':
        try:
            f = open(value[1:], "rb")
            value = f.read()
            f.close()
            if opt != "--data-binary":
                value = value.replace("\r", "")
                value = value.replace("\n", "")
        except Exception as e:
            print >> sys.stderr, "Failed to open file to read POST data: %s" % str(e)
            sys.exit(1)
    if postData is None:
        postData = value
    else:
        postData += "&" + value

def createRequest(url, options):
    request = urllib2.Request(url)
    if options.method:
        request.get_method = lambda: options.method
    return request

usage = "Usage: curl [<options>] <url>"
parser = optparse.OptionParser(usage=usage, version="1.0", prog="curl")
def parseOptions():
    parser.add_option("-i", "--include", dest="include_headers", action="store_true",
                      help="Include the HTTP-header in the  output")
    parser.add_option("-H", "--header", dest="headers", action="append",
                      help="Extra header to use when getting a web page")
    parser.add_option("-o", "--output", dest="file",
                      help="Write output to <file> instead of  stdout")
    parser.add_option("-A", "--user-agent", dest="userAgent",
                      help="Specify the User-Agent string to send to the HTTP server")
    parser.add_option("-e", "--referer", dest="referer",
                      help='Sends the "Referrer Page" information to the HTTP server')
    parser.add_option("-X", "--request", dest="method",
                      help='Uses specified HTTP method instead of GET?POST')
    parser.add_option("-d", "--data", "--data-ascii", action="callback", dest="data",
                      help="Sends specified string (or @file content) as POST request (removes \\r or \\n from the file)",
                      type="string", nargs=1,
                      callback=dataOptCallback)
    parser.add_option("--data-binary", action="callback", dest="data",
                      help="Sends specified string (or @file content) as POST request (no processing is done)",
                      type="string", nargs=1,
                      callback=dataOptCallback)

    (options, urls) = parser.parse_args()
    return (options, urls)

(options, urls) = parseOptions()

if not urls:
    print "No urls specified"

def openFile(options):
    if options.file:
        try:
            out = open(options.file, "wb")
        except Exception as e:
            print >>sys.stderr, "Failed to open %s for writing" % options.file
            print str(e)
            sys.exit(1)
    else:
        out = sys.stdout
    return out


def dumpResult(options, result, out):
    READ_SZ = 128 * 1024
    if options.include_headers:
        print >> out, str(result.headers)
    
    while True:
        data = result.read(READ_SZ)
        if not data:
            break
        out.write(data)
    out.close()

out = openFile(options)

headers = options.headers if options.headers else []

for url in urls:
    req = createRequest(url, options)
    if postData is not None:
        req.add_data(postData)
    for header in headers:
        try:
            headerName, headerValue = header.split(':', 1)
            headerValue = headerValue.lstrip()
            req.add_header(headerName, headerValue)
        except:
            print >>sys.stderr, "Invalid header %s, skipped" % header

    if options.userAgent:
        req.add_header("User-Agent", options.userAgent)
    if options.referer:
        req.add_header("Referer", options.referer)
    try:
        result = urllib2.urlopen(req)
    except urllib2.URLError as e:
        print >>sys.stderr, str(e)
        sys.exit(22)
    dumpResult(options, result, out)

if out != sys.stdout:
    out.close()

    
