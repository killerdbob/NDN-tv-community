import { toByteArray } from "base64-js";
import { Data, Name, SigType } from "@ndn/packet";
import { Decoder, Encoder } from "@ndn/tlv";
import { Certificate, createSigner, createVerifier, HMAC } from "@ndn/keychain";

function fromBase64(s: string): Uint8Array {
    return toByteArray(s.replace(/\s/g, ""));
}

const sz02 = fromBase64(`
Bv0BUAc9CARwY25sCANuZG4IBXZpZGVvCARzejAyCARsaXZlCANLRVkICDaPid6u
v4nDCARzZWxmNggAAAGAAZaR9RQJGAECGQQANu6AFVswWTATBgcqhkjOPQIBBggq
hkjOPQMBBwNCAASBSMbJ7FME/CWm48UrlHjbBpgZTqg97BQoHY3hh9qrj01gcMH7
nL2+bzv1clgaVvWrn1XdwCaADC3kpPPbEMzRFl4bAQMcLwctCARwY25sCANuZG4I
BXZpZGVvCARzejAyCARsaXZlCANLRVkICDaPid6uv4nD/QD9Jv0A/g8xOTcwMDEw
MVQwMDAwMDD9AP8PMjAyMjA0MDdUMDExNDQ2F0cwRQIhAKJf8GWBQdCJSvByLe6n
iuy/Abby6ss6ESUJdMQUSXDnAiAGbnuM4msTa9bQikcgTsbVq99OofNQaZ0Vitbs
8yJZjQ==`);
const data0 = new Decoder(sz02).decode(Data);
const cert0 = Certificate.fromData(data0);
