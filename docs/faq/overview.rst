.. _faq-overview:

===
FAQ
===

Can I use any project/team name with Freight Forwarder?
=======================================================

Yes. Just set it in the manifest/CLI and the image will be tagged and stored
appropriately.

How do I find out where the keys to my various 'containerShips' are?
====================================================================

SSL certs are required for connecting to Docker daemons. Even if you're
running Docker locally, you'll need to enable SSL support to use that
daemon.
