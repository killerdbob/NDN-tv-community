import { el } from "redom";
import shaka from "shaka-player";

import { NdnPlugin } from "./shaka-ndn-plugin.js";

shaka.polyfill.installAll();
const isBrowserSupported = shaka.Player.isBrowserSupported() &&
  !/\((?:iPhone|iPad); /.test(navigator.userAgent);
shaka.net.NetworkingEngine.registerScheme("ndn", NdnPlugin, shaka.net.NetworkingEngine.PluginPriority.FALLBACK, true);

export class Player {
  static supported = isBrowserSupported;

  constructor() {
    <video id='video-raw' this="el" controls autoplay />;
  }

  onmount() {
    this.player = new shaka.Player(this.el);
    this.entry = {}
    this.player.configure({
      playRangeEnd: Infinity,
      playRangeStart: 0,
      streaming: {
        useNativeHlsOnSafari: false,
        bufferingGoal: 100,
        // rebufferingGoal: 5,
        bufferBehind: 100,
        safeSeekOffset: 5,
        // jumpLargeGaps: true,
        lowLatencyMode: true,
        startAtSegmentBoundary: false,
        retryParameters: {
          maxAttempts: 5, //测试直播，原值为5
          timeout: 300000, //测试直播，原值为0
          baseDelay: 1000,
          backoffFactor: 4,
          fuzzFactor: 0.5,
          stallTimeout: 5000,
          // stallTimeout: 5000, //测试直播
          // baseDelay: 2000, //测试直播
        },
      },
      manifest: {
        retryParameters: {
          maxAttempts: Infinity,
          baseDelay: 1000,
          backoffFactor: 2,
          fuzzFactor: 0.5,
          timeout: 5000
        }
      }
      // manifest: {
      //   defaultPresentationDelay: 1.0,
      // }
    });
    // this.schedule_watchdoge = setInterval(() => {
    //   let raw_video = document.getElementById('video-raw');
    //   if (raw_video === null) {
    //     return;
    //   }

    //   if (raw_video.buffered.length <= 0) {
    //     // setTimeout(this.sche_watchdog(), 1000);
    //     return;
    //   }
    //   // setTimeout(this.sche_watchdog(), 1000);
    //   if (raw_video.currentTime > raw_video.buffered.end(0) + 10 || raw_video.currentTime < raw_video.buffered.start(0)) {
    //     const { name } = this.entry;
    //     this.player.load(`ndn:${name}`);
    //   }
    //   console.log('[currentTime]: ', raw_video.currentTime);
    //   console.log('[buffered]: ', raw_video.buffered.start(0), raw_video.buffered.end(0));
    //   console.log('[buffered length]: ', raw_video.buffered.length);
    // }, 3000)

    // this.sche_watchdog();
    console.log('[player] on mount');
  }

  onunmount() {
    // clearInterval(this.schedule_watchdoge);
    this.player.destroy();
    console.log(this.player);

  }

  /** @param {import("./content.js").Entry} entry */
  update(entry) {
    const { name } = entry;
    this.entry = entry;
    NdnPlugin.reset();
    // this.player.load("http://101.200.211.168:8080/live/music/playlist.m3u8");
    this.player.load(`${name}`);
    // this.player.load(`ndn:${name}`);
  }

  getStat() {
    return {
      playerStats: this.player.getStats(),
      ndnInternals: NdnPlugin.getInternals(),
    };
  }
}
