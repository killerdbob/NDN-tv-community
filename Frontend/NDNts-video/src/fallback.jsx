import embed from "embed-video";
import { el, setChildren } from "redom";

import { Player } from "./player.jsx";

const notSupported = Player.supported ? "" : "NDNts adaptive video does not support this browser. ";

export class Fallback {
  constructor() {
    <div this="el" class="fallback"/>;
  }

  /** @param {import("./content.js").Entry} entry */
  update(entry) {
    const { fallback } = entry;
    if (fallback) {
      const $div = el("div");
      $div.innerHTML = embed(fallback);
      setChildren(this.el, [
        $div,
        <p>
          {notSupported}
          You are watching from a fallback site.</p>,
      ]);
    } else {
      setChildren(this.el, [
        <p>
          {notSupported}
          Fallback site is unavailable for this content.
        </p>,
      ]);
    }
  }
}
