import { el } from "redom";

const ROUTERS = [
  ["ws://192.168.0.2:9696/", ".0.2 靶场"],
  ["ws://192.168.60.223:9696/", "PCL NDN"],
  ["ws://120.237.18.24:9696/", "PCL-NDN-Shenzhen"],
  ["ws://101.200.211.168:9696/", "PCL-NDN-Beijing"],
  ["ws://47.108.183.31:9696/", "PCL-NDN-Chengdu"],
  ["ws://47.100.82.36:9696/", "PCL-NDN-Shanghai"],
  ["ws://8.134.127.43:9696/", "PCL-NDN-Guangzhou"],
  ["ws://8.210.223.158:9696/", "PCL-NDN-Hongkong"],
  ["ws://47.88.9.244:9696/", "PCL-NDN-USA"],
];

export class Pref {
  constructor() {
    <details this="el">
      <summary>Preferences</summary>
      <form this="$form" class="pure-form pure-form-stacked">
        <fieldset>
          <label>Preferred router
            <input this="$router" size="40" placeholder="wss:// or https://"/>
          </label>
          {ROUTERS.map(([uri, name]) => (
            <label class="pure-checkbox checkbox-set-router">
              <input type="checkbox" data-set-router={uri}/> {name}
            </label>
          ))}
          <button type="submit" class="pure-button">Set</button>
        </fieldset>
      </form>
    </details>;

    this.$router.addEventListener("change", () => this.clearSetRouterCheckboxes());
    for (const checkbox of this.$form.querySelectorAll(".checkbox-set-router input")) {
      checkbox.addEventListener("change", (evt) => {
        this.clearSetRouterCheckboxes(evt.target);
        if (evt.target.checked) {
          this.$router.value = evt.target.getAttribute("data-set-router");
        }
      });
    }
    this.$form.addEventListener("submit", (evt) => {
      evt.preventDefault();
      window.localStorage.setItem("router", this.$router.value);
      location.reload();
    });
  }

  clearSetRouterCheckboxes = (except) => {
    for (const checkbox of this.$form.querySelectorAll(".checkbox-set-router input")) {
      if (checkbox !== except) {
        checkbox.checked = false;
      }
    }
  };
}
