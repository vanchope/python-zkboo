Technical assumptions:

- priv

Whenever a private variable is provided, we assume that it is correct. This is done to avoid unnecessary checks,
that may increase significantly the overall runtime.

FIXME no longer needed
For this reason, we distinguish private keys for commitment schemes, i.e., w0, w2, ..., w{N-1},
where N is the number of users.







