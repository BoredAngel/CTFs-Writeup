---
description: '[Solved] A white box web exploitation CTF challenge from Compfest 17'
---

# \[Web] (not) Simple Web

## TL;DR

* A Golang webserver  and a python proxy server
* Flag located in webserver but has a filter at the proxy server blocking direct access&#x20;
* A pinned version of hyper was used. hyper \[version] has a CVE that leads to HTTP Smuggling
* &#x20;HTTP Smuggling TE.CL to make a second HTTP request that doesn't get checked by the proxy server.
* Profit.

Flag: COMPFEST17{http\_desync\_is\_fun\_right\_06021bdb8e}

## Description

I didn't save it lmao. Next time I'll do better, I swear

## Overview

In this challenge we are given a website and a proxy server. The website is not exposed directly but only reached through the proxy. Every request is sent only to the proxy and then the proxy send it to the web server and vice versa.&#x20;

Not really much to look at in the website itself:

<figure><img src="../../.gitbook/assets/image (4).png" alt=""><figcaption></figcaption></figure>

There's only one other endpoint and it's <mark style="color:$success;">/secret.html</mark> but we can't reach it due to the proxy.

The Proxy itself is a custom proxy that the author of the challenge made.  Here's a small snippet of it:

<figure><img src="../../.gitbook/assets/image (6).png" alt=""><figcaption><p>You can check the whole code in my github repo (link below)</p></figcaption></figure>

The proxy itself is a pretty simple proxy made with python that receive request and send it to the internal server, receive the answer from the internal server and then send it back to the client.

Looking at the web server itself, it is made with rust using the hyper library. The important thing is this part of the code:

<figure><img src="../../.gitbook/assets/image (7).png" alt=""><figcaption></figcaption></figure>

So to get the flag, we really just need to make a HTTP request to /secret.html\
Unfortunately, it is being filtered by the proxy so any request to there will be rejected.

<figure><img src="../../.gitbook/assets/image (5).png" alt=""><figcaption></figcaption></figure>

I'm not sure if I am just skill issue-ed but I don't think we can bypass this

## Solution

Although It took me so long to solve this (cuz im a dummy), the solution is very simple.&#x20;

We first take a look at the library being used. while the proxy python server seems to be using latest version, the same thing cannot be said for the Rust web server:

<figure><img src="../../.gitbook/assets/image (8).png" alt=""><figcaption></figcaption></figure>

Searching up "Rust hyper 0.14.9 CVE" we can find [CVE-2021-32714](https://www.cvedetails.com/cve/CVE-2021-32714/), where it's possible for an Integer overflow to happen when decoding chunk from a request that uses the "Tranfer-Encoding: chunked" header. This vulnerability can leads to a request smuggling attack where we send two request concealed as one request.&#x20;

The attack is very simple:

{% code fullWidth="true" %}
```
GET / HTTP/1.1
Host: localhost:8000
Transfer-encoding: chunked

f0000000000000003
abc
0                             

GET /secret.html HTTP/1.1
Host: localhost:8000


```
{% endcode %}

When this request gets to the proxy server, it sees that the request  is is using the chunked transfer encoding and the chunk size is <mark style="color:orange;">f0000000000000003</mark> and so it sees the request as <mark style="color:$warning;">one big request</mark>.

But when the Rust web server see the request, it will try to decode the request like in the proxy server but upon getting the length <mark style="color:orange;">f0000000000000003</mark>  an integer overflow will happen and the server will see the length as <mark style="color:orange;">3</mark>.&#x20;

As such what the Rust server is two different HTTP request and will return the flag endpoint

<figure><img src="../../.gitbook/assets/Peek 2025-09-08 17-28.gif" alt=""><figcaption></figcaption></figure>

Flag: COMPFEST17{http\_desync\_is\_fun\_right\_06021bdb8e}

## Afterthought

Oh my god, It took me so long to solve this because I didn't immediately check for CVEs on the library being used. In hindsight it was so obvious with that comment in the Cargo.toml. Hopefully I wont forget this lesson next time I play CTFs

## Links

Source Code:

{% embed url="https://github.com/BoredAngel/CTFs-Writeup/tree/main/2025/Compfest-17/web/not_simple_web" %}

References:

{% embed url="https://nvd.nist.gov/vuln/detail/CVE-2021-32714" %}

{% embed url="https://portswigger.net/web-security/request-smuggling" %}

