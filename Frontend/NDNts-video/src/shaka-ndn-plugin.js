import { Segment as Segment1, Version as Version1 } from "@ndn/naming-convention1";
import { Segment2, Segment3, Version2, Version3 } from "@ndn/naming-convention2";
import { FwHint, Name } from "@ndn/packet";
import { discoverVersion, fetch, RttEstimator, TcpCubic } from "@ndn/segmented-object";
import { toHex } from "@ndn/tlv";
import hirestime from "hirestime";
import DefaultMap from "mnemonist/default-map.js";
// import MultiMap from "mnemonist/multi-map.js";
import PQueue from "p-queue";
import shaka from "shaka-player";

import { Decoder, Encoder, fromHex } from "@ndn/tlv";
import { Data, SigType } from "@ndn/packet";
import { Certificate, createSigner, createVerifier, HMAC, SigningAlgorithmListFull } from "@ndn/keychain";
import { toByteArray } from "base64-js";

function fromBase64(s) {
  return toByteArray(s.replace(/\s/g, ""));
}

const sz02 = fromBase64(`
Bv0BTwc9CARwY25sCANuZG4IBXZpZGVvCARzejAyCARsaXZlCANLRVkICC1Glh9A
BC8FCARzZWxmNggAAAGAKxI38RQJGAECGQQANu6AFVswWTATBgcqhkjOPQIBBggq
hkjOPQMBBwNCAATWH7tZGZbz+fuUnpx/IxoOIZ1ipAf0QWNRzkN/V71Fua2Mhds8
tGILFMLkNvKH9Njn1i85XwgRBFBBTfS3hj8PFl4bAQMcLwctCARwY25sCANuZG4I
BXZpZGVvCARzejAyCARsaXZlCANLRVkICC1Glh9ABC8F/QD9Jv0A/g8xOTcwMDEw
MVQwMDAwMDD9AP8PMjAyMjA0MTVUMDIzNDE1F0YwRAIgcn/wSGmDz7HpNR56mVGF
VLt9xR2q8Qqb0IYBhC48L0wCIBQ//+R3Ll4fZfNpJrGs1G7phhTGGCywyugL2QES
E7QO`
);

const data0 = new Decoder(sz02).decode(Data);
const cert0 = Certificate.fromData(data0);
const verifier = createVerifier(cert0);

// console.log(verifier);
// console.log(verifier);

// import { sendBeacon } from "./connect.js";

const getNow = hirestime();

/** @type {import("@ndn/packet").NamingConvention<number>} */
let segmentNumConvention;

/** @type {import("@ndn/packet").Component} */
let versionComponent;

/** @type {PQueue} */
let queue;

/** @type {RttEstimator} */
let rtte;

/** @type {TcpCubic} */
let ca;

/** @type {DefaultMap<string, number>} */
let estimatedCounts;

/** @type {DefaultMap<string, number>} */
let estimatedCountsTimestamp;
const buffer_time = 100;

// const ndnWebVideoPrefix = new Name("/ndn/web/video");
// const yoursunnyFwHint = new FwHint([new FwHint.Delegation("/yoursunny")]);

function Uint8Array2String(Data) {
  var res = "";
  for (var i = 0; i < Data.length; i++) {
    res += String.fromCharCode(Data[i]);
  }
  return res;
}

/**
 * shaka.extern.SchemePlugin for ndn: scheme.
 * @param {string} uri
 */
export function NdnPlugin(uri, request, requestType) {
  // console.log("uri: ", uri);
  // console.log("-----------------------------------------------------");
  const name = new Name(uri.replace(/^ndn:/, ""));
  const estimatedCountKey = toHex(name.getPrefix(-2).value);
  // var estimatedFinalSegNum = estimatedCounts.get(estimatedCountKey);
  var estimatedFinalSegNum = estimatedCounts.get(name.toString());
  /** @type {import("@ndn/packet").Interest.ModifyFields | undefined} */
  // const modifyInterest = ndnWebVideoPrefix.isPrefixOf(name) ? { fwHint: yoursunnyFwHint } : undefined;
  let modifyInterest = undefined;
  if (uri.endsWith('.m3u8')) {
    modifyInterest = { mustBeFresh: true };
  }

  const abort = new AbortController();
  /** @type {fetch.Result} */
  let fetchResult;

  const t0 = getNow();
  let t1 = 0;

  // estimatedCountsTimestamp.set(name.toString(), t0); //[修复] 增加时间监控



  // console.log(estimatedCounts);


  // log.debug(`NdnPlugin.request ${name} queued=${queue.size}`);
  // console.log(`NdnPlugin.request ${name} queued=${queue.size}`)
  return new shaka.util.AbortableOperation(
    queue.add(async () => {
      t1 = getNow();
      // log.debug(`NdnPlugin.fetch ${name} waited=${Math.round(t1 - t0)}`);
      // console.log(`NdnPlugin.fetch ${name} waited=${Math.round(t1 - t0)}`)
      if (!segmentNumConvention) {
        // console.log('start get version');
        const versioned = await discoverVersion(name, {
          conventions: [
            [Version3, Segment3],
            [Version2, Segment2],
            [Version1, Segment1],
          ],
          modifyInterest,
          signal: abort.signal,
        });
        // console.log('get version');
        versionComponent = versioned.get(-1);
        segmentNumConvention = versioned.segmentNumConvention;
        // console.log('versionComponent: ', versionComponent)
        // log.info(`NdnPlugin.discoverVersion version=${versioned.versionConvention.parse(versionComponent)}`);
        // console.log("version:", versioned.versionConvention.parse(versionComponent))
        t1 = getNow();
      }

      // console.log(name.append(versionComponent).toString());
      // console.log("estimatedFinalSegNum:", estimatedFinalSegNum)

      //clean buffer
      for (let key of estimatedCountsTimestamp.keys()) {
        let pretime = estimatedCountsTimestamp.get(key)
        if (pretime + buffer_time * 1000 < t1) {
          estimatedCountsTimestamp.delete(key);
          estimatedCounts.delete(key);
        }
      }
      fetchResult = fetch(name.append(versionComponent), {
        rtte,
        ca,
        retxLimit: 5,
        segmentNumConvention,
        modifyInterest,
        estimatedFinalSegNum,
        signal: abort.signal,
        // verifier: await verifier
      });
      const updateDataToCallback = async() => {
        const data = await fetchResult;
        // console.log((await verifier).verify(data));
        if (request.streamDataCallback) {
          await request.streamDataCallback(data);
        }
        return data;
      }
      return updateDataToCallback();
    }).then(
      (payload) => {
        const timeMs = getNow() - t1;
        // estimatedCounts.set(estimatedCountKey, fetchResult.count);
        // estimatedCounts.set(name.toString(), fetchResult.count); //[修复] 增加final估计

        // log.debug(`NdnPlugin.response ${name} rtt=${Math.round(timeMs)} count=${fetchResult.count}`);
        // sendBeacon({
        //   a: "F",
        //   n: name.toString(),
        //   d: Math.round(timeMs),
        //   sRtt: Math.round(rtte.sRtt),
        //   rto: Math.round(rtte.rto),
        //   cwnd: Math.round(ca.cwnd),
        // });
        // let payload_str = Uint8Array2String(payload)
        // console.log(payload_str);

        // console.log({
        //   uri,
        //   originalUri: uri,
        //   data: payload_str,
        //   headers: {},
        //   timeMs,
        // })

        console.log('finish:', uri, payload.length, timeMs)
        return {
          uri,
          originalUri: uri,
          data: payload,
          headers: {},
          timeMs,
        };
      },
      (err) => {
        if (abort.signal.aborted) {
          // log.debug(`NdnPlugin.abort ${name}`);
          return shaka.util.AbortableOperation.aborted();
        }
        // log.warn(`NdnPlugin.error ${name} ${err}`);
        console.log(err.toString())
        // sendBeacon({
        //   a: "E",
        //   n: name.toString(),
        //   err: err.toString(),
        // });
        throw new shaka.util.Error(
          shaka.util.Error.Severity.RECOVERABLE,
          shaka.util.Error.Category.NETWORK,
          shaka.util.Error.Code.HTTP_ERROR,
          uri, 503, null, {}, requestType);
      },
    ),
    async () => abort.abort(),
  );
}

NdnPlugin.reset = () => {
  segmentNumConvention = undefined;
  versionComponent = undefined;
  queue = new PQueue({ concurrency: 4 });
  rtte = new RttEstimator({ maxRto: 10000 });
  ca = new TcpCubic({ c: 0.1 });
  estimatedCounts = new DefaultMap(() => 5);
  estimatedCountsTimestamp = new DefaultMap(() => 0);
};

NdnPlugin.getInternals = () => {
  return { queue, rtte, ca };
};

NdnPlugin.reset();
