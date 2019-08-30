- Hongbo Chen
- hc50@iu.edu

# Task 1
## What is the IP address of youc computer? Of the gaia.cs.umass.edu server?
- IP of my computer: Source: 156.56.158.145
- IP of the server: Destination: 128.119.245.12

## What is the status code and phrase returned from the server to your browser?
- Status Code: 304
- Status phrase: Not Modified

## What languages does your browser indicate to the server that it can accept? Which header line is used to indicate this information?
- The browser accepts English and Chinese.
- From this line in the request headers: *Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7*

## How many bytes of content (size of file) are returned to your browser? Which header line is used to indicate this information?
- From wireshark's TCP section, we can see: *TCP payload (239 bytes)*. So the content(including headers) size returend to my browser is 239 bytes. But the size of html file is 128B. In http protocol, there **should** be "Content-Length" indicating the size returedn to the browser, but it seems that our website doesn't use it.
- In TCP section in wireshark, you can see: *[TCP Segment Len: 239]*, or *TCP payload (239 bytes)* indicating the size.

## How long did it take from when the HTTP GET message was sent until the HTTP OK reply was received?\
- *[Time since request: 0.031207211 seconds]*
- It takes 0.031207211 second.

# Task 2
## Output from traceroute
traceroute to yahoo.com (72.30.35.9), 30 hops max, 60 byte packets
 1  xe-1-3-3.1915.cr5.bldc.net.uits.iu.edu (156.56.158.2)  5.132 ms  5.063 ms  5.075 ms
 2  ae-15.0.br2.bldc.net.uits.iu.edu (134.68.3.74)  0.362 ms  0.357 ms  0.337 ms
 3  ae-4.12.rtr.ll.indiana.gigapop.net (149.165.183.13)  2.372 ms  2.359 ms  2.346 ms
 4  et-1-3-0.1.rtr.ictc.indiana.gigapop.net (149.165.255.193)  2.813 ms  2.847 ms  2.914 ms
 5  lo-0.1.rtr2.chic.indiana.gigapop.net (149.165.255.6)  8.525 ms  6.867 ms  6.882 ms
 6  et-1-1-0.2290.sw2.600wchicag.omnipop.btaa.org (149.165.183.90)  6.771 ms  6.690 ms  6.673 ms
 7  r-equinix-isp-ae2-2275.wiscnet.net (140.189.9.137)  6.855 ms  6.861 ms  6.856 ms
 8  * * *
 9  ae-9.pat2.bfz.yahoo.com (216.115.101.199)  19.500 ms ae-8.pat1.bfz.yahoo.com (216.115.101.231)  25.785 ms ae-10.pat2.bfy.yahoo.com (184.165.16.0)  19.176 ms
10  et-19-1-0.msr1.bf2.yahoo.com (74.6.227.147)  29.461 ms et-1-1-1.msr1.bf1.yahoo.com (74.6.227.135)  29.473 ms et-1-1-1.msr1.bf2.yahoo.com (72.30.223.53)  19.534 ms
11  et-19-0-0.clr1-a-gdc.bf1.yahoo.com (74.6.122.33)  20.249 ms et-0-1-0.clr2-a-gdc.bf1.yahoo.com (74.6.122.17)  19.732 ms UNKNOWN-74-6-122-X.yahoo.com (74.6.122.91)  19.609 ms
12  eth-17-3.bas1-1-flk.bf1.yahoo.com (98.137.192.151)  29.770 ms et-19-0-0.clr2-a-gdc.bf1.yahoo.com (74.6.122.37)  28.014 ms eth-18-3-bas1-1-flk.bf1.yahoo.com (98.139.128.73)  29.803 ms
13  media-router-fp1.prod1.media.vip.bf1.yahoo.com (72.30.35.9)  28.054 ms  28.072 ms  28.054 ms

