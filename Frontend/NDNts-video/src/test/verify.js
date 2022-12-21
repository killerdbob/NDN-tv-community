let base64_js_1 = await import("base64-js");
let packet = await import("@ndn/packet");
let tlv = await import("@ndn/tlv");
let keychain = await import("@ndn/keychain");
function fromBase64(s) {
    return (0, base64_js_1.toByteArray)(s.replace(/\s/g, ""));
}
var sz02 = fromBase64("\n        Bv0BUAc9CARwY25sCANuZG4IBXZpZGVvCARzejAyCARsaXZlCANLRVkICDaPid6u\n        v4nDCARzZWxmNggAAAGAAZaR9RQJGAECGQQANu6AFVswWTATBgcqhkjOPQIBBggq\n        hkjOPQMBBwNCAASBSMbJ7FME/CWm48UrlHjbBpgZTqg97BQoHY3hh9qrj01gcMH7\n        nL2+bzv1clgaVvWrn1XdwCaADC3kpPPbEMzRFl4bAQMcLwctCARwY25sCANuZG4I\n        BXZpZGVvCARzejAyCARsaXZlCANLRVkICDaPid6uv4nD/QD9Jv0A/g8xOTcwMDEw\n        MVQwMDAwMDD9AP8PMjAyMjA0MDdUMDExNDQ2F0cwRQIhAKJf8GWBQdCJSvByLe6n\n        iuy/Abby6ss6ESUJdMQUSXDnAiAGbnuM4msTa9bQikcgTsbVq99OofNQaZ0Vitbs\n        8yJZjQ==");
var data0 = new tlv.Decoder(sz02).decode(packet.Data);
var cert0 = keychain.Certificate.fromData(data0);
