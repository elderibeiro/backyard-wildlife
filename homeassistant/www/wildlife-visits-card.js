/**
 * Wildlife Visits card
 *
 * Extends LLM Vision's timeline card so Recent Visits can show a crop around
 * the animal. The automation stores a tag at the end of the event description:
 *   [crop:ymin,xmin,ymax,xmax]
 * with Gemini-style 0-1000 coordinates. When the box is missing, the full
 * key frame is shown instead.
 *
 * Install LLM Vision and its lovelace card first, then add this file as a
 * dashboard resource (type: module).
 */
(() => {
  const TAG = "wildlife-visits-card";
  const RE = /\[crop:\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\]\s*$/i;

  function cropUrl(url, box) {
    const [ymin, xmin, ymax, xmax] = box;
    return new Promise((resolve) => {
      const img = new Image();
      img.crossOrigin = "anonymous";
      img.onload = () => {
        try {
          const w = img.naturalWidth;
          const h = img.naturalHeight;
          const pad = 0.18;
          const py = (ymax - ymin) * pad;
          const px = (xmax - xmin) * pad;
          let top = Math.max(0, Math.floor((h * (ymin - py)) / 1000));
          let left = Math.max(0, Math.floor((w * (xmin - px)) / 1000));
          let bottom = Math.min(h, Math.ceil((h * (ymax + py)) / 1000));
          let right = Math.min(w, Math.ceil((w * (xmax + px)) / 1000));
          const side = Math.max(bottom - top, right - left, 80);
          const cx = Math.floor((left + right) / 2);
          const cy = Math.floor((top + bottom) / 2);
          left = Math.max(0, Math.min(w - side, cx - Math.floor(side / 2)));
          top = Math.max(0, Math.min(h - side, cy - Math.floor(side / 2)));
          const out = Math.min(512, Math.max(side, 160));
          const c = document.createElement("canvas");
          c.width = out;
          c.height = out;
          const g = c.getContext("2d");
          g.imageSmoothingEnabled = true;
          g.imageSmoothingQuality = "high";
          g.drawImage(img, left, top, side, side, 0, 0, out, out);
          c.toBlob((bl) => resolve(bl ? URL.createObjectURL(bl) : url), "image/jpeg", 0.9);
        } catch (err) {
          resolve(url);
        }
      };
      img.onerror = () => resolve(url);
      img.src = url;
    });
  }

  customElements.whenDefined("llmvision-card").then(() => {
    if (customElements.get(TAG)) return;
    const Base = customElements.get("llmvision-card");
    class WildlifeVisitsCard extends Base {
      async fetchEvents(hass, opts) {
        const items = await super.fetchEvents(hass, opts);
        if (!Array.isArray(items)) return items;
        this._wlCrops = this._wlCrops || new Map();
        return items.map((event) => {
          const text = event.description || "";
          const match = RE.exec(text);
          if (match) {
            const box = match.slice(1, 5).map(Number);
            if (event.keyFrame && box[2] > box[0] && box[3] > box[1]) {
              this._wlCrops.set(event.keyFrame, box);
            }
            event.description = text.slice(0, match.index).trimEnd();
          }
          return event;
        });
      }

      resolveKeyFrame(hass, keyFrame) {
        const base = super.resolveKeyFrame(hass, keyFrame);
        const box = this._wlCrops && this._wlCrops.get(keyFrame);
        if (!box) return base;
        this._wlCache = this._wlCache || new Map();
        if (!this._wlCache.has(keyFrame)) {
          this._wlCache.set(
            keyFrame,
            base.then((url) => (url ? cropUrl(url, box) : url)).catch(() => base)
          );
        }
        return this._wlCache.get(keyFrame);
      }
    }
    customElements.define(TAG, WildlifeVisitsCard);
    window.customCards = window.customCards || [];
    window.customCards.push({
      type: TAG,
      name: "Wildlife Visits (cropped)",
      description: "LLM Vision timeline that crops each visit around the animal",
    });
  });
})();
