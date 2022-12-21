import { el, mount, router } from "redom";

import { Catalog } from "./catalog.jsx";
import { connect } from "./connect.js";
import { fetchContent, makeIncompleteEntry } from "./content.js";
import { Fallback } from "./fallback.jsx";
import { Playback } from "./playback.jsx";




/** @type {import("./content.js").Content} */
let content;

const app = router(".app", {
  catalog: Catalog,
  play: Playback,
  fallback: Fallback,
});

class Main {
  constructor() {
    <div this="el">
      {app}
      <footer>
        <a href="#">{content.sitename}</a>, powered by <a href="https://github.com/yoursunny/NDNts-video" target="_blank" rel="noopener">NDNts adaptive video</a>
      </footer>
    </div>;

    connect();
  }
}

function gotoPage() {
  const { sitename, catalog } = content;
  document.title = sitename;
  let [action, param] = location.hash.split("=", 2);
  action = action.slice(1);
  switch (action) {
    case "play":
    case "fallback": {
      const entry = catalog.find((entry) => entry.name === param) ?? makeIncompleteEntry(param);
      if (entry.title) {
        document.title = `${entry.title} - ${sitename}`;
      }
      // console.log(entry)
      app.update(action, entry);
      break;
    }
    case "tag":
      app.update("catalog", { content, tag: param });
      break;
    default:
      app.update("catalog", { content, tag: undefined });
      break;
  }
}

// export async function CertBase64(d, filename) {
//   const data = await inputBase64(Data, filename);
//   Certificate.fromData(data);
//   const read = filename ? fs.readFile(filename, { encoding: "utf-8" }) : getStdin();
//   const wire = Buffer.from(await read, "base64");
//   new Decoder(wire).decode(d);


// }



// const [, key] = await generateSigningKey("/H/KEY/x", HMAC,{
//   importRaw: fromHex("123456@pcl"),
// })

// let certBase64Data = `Bv0BGwciCAFBCANLRVk4CAAF3Gv+Md9wCARzZWxmNggAAAGAG6VtGhQJGAECGQQANu6AFVswWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAASohRfYm+p3mQGJRcMh/NNSST5hHlIJbxbEomzQVRtz2xL055drA/LCVm+p0Sy9Dey/RDUUbcZQo7xYT4ZbeM9kFkMbAQMcFAcSCAFBCANLRVk4CAAF3Gv+Md9w/QD9Jv0A/g8xOTg3MDIxMlQwNjMwMDD9AP8POTk5OTEyMzFUMjM1OTU5F0gwRgIhANeCiZNcoI3CQ0+J5ZJKiVaV7R8Fcxqp7GCYOf+hQCEjAiEAy8bqoU1CCW2CP1rUrTEk/uIPR2KUMLXPwAofyKO7Dp8=`
// async function inputBase64(d, Base64Data) {
//   const wire = base64ToUint8Array(Base64Data);
//   return wire;
//   // return new Decoder(wire).decode(d);
// }
// async function inputCertBase64(Base64Data) {
//   const data = await inputBase64(Data, Base64Data);
//   return Certificate.fromData(data);
// }

// let cert = inputCertBase64(certBase64Data);
// let verifier = createVerifier(HMAC, cert.publicKeySpki());


(async () => {
  content = await fetchContent();
  mount(document.body, new Main());

  window.addEventListener("hashchange", gotoPage);
  gotoPage();
})();
