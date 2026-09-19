/**
 * sovereign-sdk.js — Lovetta Lane Constellation Sovereign Ed25519 Token SDK
 * Manages patron authorization headers and token-format verification across
 * constellation sites. NOTE: verification here is FORMAT verification (the
 * 64-byte Ed25519 signature shell), not signature validation — the promise
 * of offline signature checking belongs to the server, and this file never
 * claims a signature it cannot keep.
 */
(function (global) {
  "use strict";

  const STORAGE_KEY = "vkd_sovereign_token";
  const PREFIX = /^Sovereign\s+/i;

  // base64 → binary, safe in browser AND in the corridor (node:vm)
  function decode64(s) {
    if (typeof atob === "function") return atob(s);
    if (typeof Buffer !== "undefined") return Buffer.from(s, "base64").toString("binary");
    throw new Error("sovereign-sdk: no base64 decoder available");
  }

  const SovereignSDK = {
    /**
     * Get the active Sovereign token from localStorage ("" when absent).
     */
    getToken: function () {
      try {
        return localStorage.getItem(STORAGE_KEY) || "";
      } catch (e) {
        return "";
      }
    },

    /**
     * Save a Sovereign token to localStorage. The "Sovereign " prefix is
     * normalized away so the auth header never doubles it.
     */
    setToken: function (token) {
      if (!token || typeof token !== "string") return false;
      const cleanToken = token.trim().replace(PREFIX, "");
      if (!cleanToken) return false;
      try {
        localStorage.setItem(STORAGE_KEY, cleanToken);
        this.updateBadgeUI();
        return true;
      } catch (e) {
        return false;
      }
    },

    /**
     * Clear the saved token.
     */
    clearToken: function () {
      try {
        localStorage.removeItem(STORAGE_KEY);
      } catch (e) {
        /* storage unavailable — nothing to clear */
      }
      this.updateBadgeUI();
    },

    /**
     * Authorization header for fetch requests, or {} when locked.
     */
    getAuthHeader: function () {
      const token = this.getToken();
      if (!token) return {};
      return { Authorization: "Sovereign " + token };
    },

    /**
     * True when a structurally valid token is stored.
     */
    isUnlocked: function () {
      return this.verifyFormat(this.getToken());
    },

    /**
     * Format verification: base64 decoding yields at least 64 bytes (an
     * Ed25519 signature) with a UTF-8 payload following.
     */
    verifyFormat: function (token) {
      if (!token || typeof token !== "string") return false;
      try {
        const decoded = decode64(token.trim().replace(PREFIX, ""));
        return decoded.length >= 64;
      } catch (e) {
        return false;
      }
    },

    /**
     * Prompt the user to enter or swap their Sovereign Key.
     */
    promptKeyModal: function () {
      const currentToken = this.getToken();
      const input = prompt(
        currentToken
          ? "Sovereign Key Active! Paste a new key or press OK to keep current key:"
          : "Enter your Lovetta Lane Sovereign Key (vkd_sk_... or Base64 Ed25519 Token):",
        currentToken
      );
      if (input !== null && input.trim() !== "") {
        if (this.setToken(input.trim())) {
          alert("✨ Sovereign Key activated! God Mode & 24-bit WAV Master Stems Unlocked.");
        } else {
          alert("❌ Invalid key format.");
        }
      }
    },

    /**
     * Reflect the unlock state on the fixed badge — BOTH directions, so a
     * cleared key visibly locks the badge again.
     */
    updateBadgeUI: function () {
      const badge = document.getElementById("lovetta-sovereign-badge");
      if (!badge) return;
      if (this.isUnlocked()) {
        badge.style.borderColor = "#62e6c9";
        badge.style.color = "#62e6c9";
        badge.innerHTML = `<span style="display:inline-block; width:8px; height:8px; background:#62e6c9; border-radius:50%; box-shadow: 0 0 8px #62e6c9;"></span><span style="font-weight:bold;">SOVEREIGN GOD MODE ACTIVE (STEMS UNLOCKED)</span>`;
      } else {
        badge.style.borderColor = "";
        badge.style.color = "";
        badge.innerHTML = "SOVEREIGN";
      }
    }
  };

  global.SovereignSDK = SovereignSDK;

  document.addEventListener("DOMContentLoaded", function () {
    SovereignSDK.updateBadgeUI();
    const badge = document.getElementById("lovetta-sovereign-badge");
    if (badge) {
      badge.addEventListener("click", function (e) {
        e.preventDefault();
        SovereignSDK.promptKeyModal();
      });
    }
  });

})(typeof window !== "undefined" ? window : this);