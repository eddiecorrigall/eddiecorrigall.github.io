+++
title = 'HTTP Sessions'
date = 2018-12-08T16:09:59-04:00
tags = ['http', 'session', 'cookie', 'state']
draft = false

ShowReadingTime = true
ShowWordCount = true

UseHugoToc = true
ShowToc = true
TocOpen = true

[cover]
image = '/posts/http-sessions/cover.png'
alt = 'HTTP sessions cover image'
caption = ''
relative = false
+++

As an introduction, lets find out what it means to be stateless and stateful protocol. Then lets dive into how using cookies helps us maintain a server-side session, and finally lets talk about security.

## Stateless HTTP
Originally HTTP began as a stateless protocol, which will not assume any special meaning between requests even if they originate from the same socket. While this is great for serving content, it only offers a generic user experience as the server is unable to distinguish between users natively.

## Stateful HTTP
With stateful protocol, the user state is persisted between requests so the server will be able to build context. For example, server would then be able to answer: Who are they? Are they authenticated? What items do they have in their chart? In constrast, a stateless protocol would handle each request as if it had seen it for the first time.

## How cookies are set
In the HTTP response the server can optionally include a cookie as part of the header. The browser can optionally interpret and store this locally.

**Example 1: HTTP response containing two cookies**

A response containing two cookies: `yummy_cookie` with value `choco` and `tasty_cookie` with value `strawberry`.
```
HTTP/1.0 200 OK
Content-type: text/html
Set-Cookie: yummy_cookie=choco
Set-Cookie: tasty_cookie=strawberry

[page content]
```

Next time the browser requests, it will include all the cookies associated with the domain that sent them as a response. Here is what the next request might look like.

**Example 2: HTTP request containing two cookies**
```
GET /sample_page.html HTTP/1.1
Host: www.example.org
Cookie: yummy_cookie=choco; tasty_cookie=strawberry
```

As you can see, stateful HTTP contains additional header information per request. Now the server can assign a user a cookie with a value, and get the cookie back from the user, so the server can maintain a user state over time. Which no doubt consumes more resources, both on the server-side and client-side.

Not only can you send a cookie value, but you can also set a number of attributes. A detailed explanation for these attributes will come later, but for now, lets talk about HTTP sessions.

## HTTP Sessions
Cookies offer client-side storage which is often used to store a user identifier called a session identifier. Session referres to the resources allocated on the server-side to handle requests from a particular user.

When a server receives a request, it will check if the request contains a cookie with a session identifier. If the cookie exists, then it matches the identifier to a particular session. Otherwise it generates a new session and associated session identifier to pass back to the user.

Since the client can now identify itself per request, the server can maintain user state on its side. This is useful for shopping carts, user authorization, game score, etc.

## Cookie Attributes
In addition to a cookie value, there are three very important attributes: `Expires`, `HttpOnly` and `Secure`.

### Expires
Cookies can either live forever, or have a time-to-live. This is configured from the server-side by setting `Expires` to a date in the future. The browser will cleanup any cookies that have expired. It is best to set a reasonable time frame for cookies that contain sensitive information, otherwise if the cookie is hijacked, then it makes it even more difficult to contain the problem.

#### Session timeout

Do not confuse cookie expiration with session timeout. Session timeout is the maximum time a session can be inactive before the server is allowed to free its resources and invalidate. Remember the server maintains its own resources on the server-side. If they are not cleaned up then the server will eventually run out of mememory, preventing any new requests from being handled.

A short session timeout of 15 minutes is reasonable. A user can then be inactive for up to 15 minutes before sending another request, which then resets the timeout back to 15 minutes. Any inactivity beyond the session timeout the user session is freed and invalidated (including the session identifier cookie). The user would then have to authenticate again to have its session identifier associated with the user account.

Ideally the session cookie expiry should be set further in the future then the server session timeout. Otherwise the server session resources will still exist while it is not possible to use the session cookie to gain access. A reasonable cookie expiration is 60 minutes. That allows an authenticated user to interact with the server for up to 60 minutes before having to authenticate again.

### HttpOnly
Enabling `HttpOnly` signals to the browser that the cookie must not be exposed to JavaScript `document.cookie`. Only the server can issue cookies. Without this attribute, [cross-site scripting](https://developer.mozilla.org/en-US/docs/Glossary/Cross-site_scripting) (XSS) cannot gain access to the session identifier since the browser will actively block the attempt.

### Secure
Enabling `Secure` tells the browser to only use secure channels (HTTPS) to communicate the cookie -- keep it secure. If HTTP request / response were to pass through an unsecure network, ie. and internet cafe, then an observer can see the cookie on its way to the server and back. If malicious, the observer can use the cookie to masquerade as the user. Please see [man-in-the-middle attack](https://en.wikipedia.org/wiki/Man-in-the-middle_attack) for more information.

When testing, it is not always possible to use a secure channel, so only enable `Secure` in production.

## Authentication
A user can receive a session identifier cookie without authenticating. Once the server has authenticated the user it will use the corresponding session id provided as a means to determine if the user is authenticated.

### How does it work?
1. User agent (browser) sends HTTP request
    ```
    GET /login.html HTTP/1.1
    Host: www.example.org
    ```
2. Server sends HTTP response, after generating a session and session UUID
    ```
    HTTP/1.0 200 OK
    Content-type: text/html
    Set-Cookie: SESSIONID=7db6e400-f9a8-11e8-b568-0800200c9a66; Secure; HttpOnly; Expires=Sat, 6 Apr 2019 01:23:45 GMT;

    [login.html content]
    ```
3. User agent stores cookie, and user fills out login form
4. User clicks on sign on, which fires HTTP request
    ```
    POST /signin HTTP/1.1
    Host: www.example.org
    Cookie: SESSIONID=7db6e400-f9a8-11e8-b568-0800200c9a66

    username=eddie
    password=password
    ```
5. Server authenticates, associates `SESSIONID` with username eddie, and responses

## Why does it work?
The server generates a session identifier in such a way that the probability of it responding with `Set-Cookie` to one or more users with the same identifier is close to 0%. For this reason, it is paramount that the [random number generator](https://en.wikipedia.org/wiki/Random_number_generation) on the server is sufficiently random, otherwise security cannot be guaranteed. Think of the session identifier as a temporary access key to access the session resources. If a user guesses correctly they can gain access to an account. It is therefore the responsibility of the server to select a access key from a domain that is so large that it is nearly impossible for a user to guess an access key.

To circumvent authentication, a malicious user must guess a session ID. Often a [UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier) (a random distribution) is used as the ID. The probability of collision is equivalent to generating 1 billion UUIDs per second for about 85 years.

In addition, a user most likely needs to provide metadata (ie username) about the authenticated user, which makes a guessing approach infeasible.

Now given a session identifier, say from an insecure network, this makes it very easy to gain access since the transport of the session information is visible to anyone monitoring the network.

### Recommendations
- Set `Expires` to 60 minutes forward.
- Configure server session timeout to 15 minutes.
- Session cookie expiry should be further in the future than the server session.
- Set `HttpOnly` to prevent XSS.
- Set `Secure` in a production environment to prevent man-in-the-middle attacks.
- Ensure the session identifier generator is sufficiently random
