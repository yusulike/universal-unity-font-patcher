using System;
using System.IO;
using System.Collections.Generic;
using BepInEx;
using BepInEx.Configuration;
using BepInEx.Logging;
using UnityEngine;
using UnityEngine.SceneManagement;
using TMPro;

namespace UniversalUnityKoreanFont
{
    [BepInPlugin("com.universal.unitykoreanfont", "Universal Unity Korean Font Replacer", "1.0.0")]
    public class UniversalFontPlugin : BaseUnityPlugin
    {
        public static ManualLogSource Log { get; private set; }

        private ConfigEntry<string> _configBoldKeywords;
        private ConfigEntry<string> _configLightKeywords;
        private ConfigEntry<bool> _configOverrideDirectFont;
        private ConfigEntry<float> _configCheckInterval;
        private ConfigEntry<int> _configMaxChecks;
        private ConfigEntry<KeyCode> _configReloadKey;

        private static TMP_FontAsset _boldFontAsset;
        private static TMP_FontAsset _regularFontAsset;

        private float _timer = 0f;
        private int _checkCount = 0;

        private void Awake()
        {
            Log = Logger;
            Log.LogInfo("==========================================================");
            Log.LogInfo("[UniversalFont] Initializing Universal Unity Korean Font...");
            Log.LogInfo("==========================================================");

            // Bind Configurations
            _configBoldKeywords = Config.Bind("General", "BoldKeywords", "bold,semibold,black,heavy,norse,title,header,heading", "Comma-separated keywords to identify bold/title fonts");
            _configLightKeywords = Config.Bind("General", "LightKeywords", "light,thin,regular,normal,book", "Comma-separated keywords to identify regular/light fonts");
            _configOverrideDirectFont = Config.Bind("General", "OverrideDirectFont", false, "If true, directly changes text.font on all UI elements in addition to Fallback injection");
            _configCheckInterval = Config.Bind("General", "CheckIntervalSeconds", 2.0f, "Interval between periodic checks for newly loaded UI assets");
            _configMaxChecks = Config.Bind("General", "MaxPeriodicChecks", 30, "Maximum number of periodic checks per scene");
            _configReloadKey = Config.Bind("General", "ReloadKey", KeyCode.F10, "Hot-reload key to re-scan and re-apply fonts in real time");

            LoadFonts();

            SceneManager.sceneLoaded += OnSceneLoaded;
        }

        private void OnDestroy()
        {
            SceneManager.sceneLoaded -= OnSceneLoaded;
        }

        private void OnSceneLoaded(Scene scene, LoadSceneMode mode)
        {
            Log.LogInfo("[UniversalFont] Scene loaded: " + scene.name + " (" + scene.buildIndex + "). Re-applying font fallbacks...");
            _checkCount = 0;
            _timer = 0f;
            ApplyFontFallbacks();
        }

        private void Update()
        {
            // Hot-reload check
            if (Input.GetKeyDown(_configReloadKey.Value))
            {
                Log.LogInfo("[UniversalFont] Hot-reload key pressed! Reloading fonts...");
                LoadFonts();
                ApplyFontFallbacks();
            }

            if (_boldFontAsset == null && _regularFontAsset == null) return;
            if (_checkCount >= _configMaxChecks.Value) return;

            _timer += Time.deltaTime;
            if (_timer >= _configCheckInterval.Value)
            {
                _timer = 0f;
                _checkCount++;
                ApplyFontFallbacks();
            }
        }

        public void LoadFonts()
        {
            _boldFontAsset = null;
            _regularFontAsset = null;

            // Search directories
            List<string> searchDirs = new List<string>
            {
                Path.Combine(Paths.PluginPath, "Fonts"),
                Paths.PluginPath,
                Path.Combine(Paths.GameRootPath, "Fonts")
            };

            List<string> foundFontFiles = new List<string>();
            foreach (string dir in searchDirs)
            {
                if (Directory.Exists(dir))
                {
                    foundFontFiles.AddRange(Directory.GetFiles(dir, "*.ttf", SearchOption.TopDirectoryOnly));
                    foundFontFiles.AddRange(Directory.GetFiles(dir, "*.otf", SearchOption.TopDirectoryOnly));
                }
            }

            if (foundFontFiles.Count == 0)
            {
                Log.LogWarning("[UniversalFont] No .ttf or .otf font files found in search directories.");
                return;
            }

            Log.LogInfo("[UniversalFont] Found " + foundFontFiles.Count + " font files.");

            string boldPath = null;
            string regularPath = null;

            string[] boldKeys = _configBoldKeywords.Value.Split(new char[] { ',' }, StringSplitOptions.RemoveEmptyEntries);
            string[] lightKeys = _configLightKeywords.Value.Split(new char[] { ',' }, StringSplitOptions.RemoveEmptyEntries);

            // Match bold and regular files
            foreach (string file in foundFontFiles)
            {
                string lowerName = Path.GetFileNameWithoutExtension(file).ToLower();

                bool isBold = false;
                foreach (string k in boldKeys)
                {
                    if (lowerName.Contains(k.Trim().ToLower()))
                    {
                        isBold = true;
                        break;
                    }
                }

                if (isBold && boldPath == null)
                {
                    boldPath = file;
                    continue;
                }

                bool isLight = false;
                foreach (string k in lightKeys)
                {
                    if (lowerName.Contains(k.Trim().ToLower()))
                    {
                        isLight = true;
                        break;
                    }
                }

                if (isLight && regularPath == null)
                {
                    regularPath = file;
                    continue;
                }

                if (regularPath == null && !isBold)
                {
                    regularPath = file;
                }
            }

            // Fallbacks if one is missing
            if (boldPath == null && regularPath != null) boldPath = regularPath;
            if (regularPath == null && boldPath != null) regularPath = boldPath;

            if (boldPath != null)
            {
                _boldFontAsset = CreateTmpFontFromFile(boldPath, "Bold");
            }
            if (regularPath != null && regularPath != boldPath)
            {
                _regularFontAsset = CreateTmpFontFromFile(regularPath, "Regular");
            }
            else
            {
                _regularFontAsset = _boldFontAsset;
            }

            Log.LogInfo("[UniversalFont] Font configuration loaded: Bold=" + (_boldFontAsset != null ? _boldFontAsset.name : "null") + 
                        ", Regular=" + (_regularFontAsset != null ? _regularFontAsset.name : "null"));
        }

        private TMP_FontAsset CreateTmpFontFromFile(string filePath, string tag)
        {
            try
            {
                Font unityFont = new Font(filePath);
                unityFont.name = Path.GetFileNameWithoutExtension(filePath);

                TMP_FontAsset tmpAsset = TMP_FontAsset.CreateFontAsset(unityFont);
                tmpAsset.name = unityFont.name + " [" + tag + "] SDF";
                Log.LogInfo("[UniversalFont] Successfully created dynamic TMP_FontAsset: " + tmpAsset.name + " from " + filePath);
                return tmpAsset;
            }
            catch (Exception ex)
            {
                Log.LogError("[UniversalFont] Error creating font from " + filePath + ": " + ex.Message);
                return null;
            }
        }

        public void ApplyFontFallbacks()
        {
            if (_boldFontAsset == null && _regularFontAsset == null) return;

            try
            {
                TMP_FontAsset[] allFonts = Resources.FindObjectsOfTypeAll<TMP_FontAsset>();
                int modifiedCount = 0;

                string[] boldKeys = _configBoldKeywords.Value.Split(new char[] { ',' }, StringSplitOptions.RemoveEmptyEntries);

                foreach (TMP_FontAsset font in allFonts)
                {
                    if (font == null || font == _boldFontAsset || font == _regularFontAsset) continue;

                    string fName = font.name != null ? font.name.ToLower() : "";
                    bool isBold = false;
                    foreach (string k in boldKeys)
                    {
                        if (fName.Contains(k.Trim().ToLower()))
                        {
                            isBold = true;
                            break;
                        }
                    }

                    TMP_FontAsset primary = isBold ? (_boldFontAsset ?? _regularFontAsset) : (_regularFontAsset ?? _boldFontAsset);
                    TMP_FontAsset secondary = isBold ? _regularFontAsset : _boldFontAsset;

                    if (font.fallbackFontAssetTable == null)
                    {
                        font.fallbackFontAssetTable = new List<TMP_FontAsset>();
                    }

                    bool modified = false;

                    // Ensure secondary fallback is present
                    if (secondary != null && secondary != primary && !font.fallbackFontAssetTable.Contains(secondary))
                    {
                        font.fallbackFontAssetTable.Insert(0, secondary);
                        modified = true;
                    }

                    // Ensure primary fallback is at index 0 (top priority)
                    if (primary != null)
                    {
                        if (!font.fallbackFontAssetTable.Contains(primary))
                        {
                            font.fallbackFontAssetTable.Insert(0, primary);
                            modified = true;
                        }
                        else if (font.fallbackFontAssetTable.IndexOf(primary) > 0)
                        {
                            font.fallbackFontAssetTable.Remove(primary);
                            font.fallbackFontAssetTable.Insert(0, primary);
                            modified = true;
                        }
                    }

                    if (modified) modifiedCount++;
                }

                // Global TMP_Settings
                if (TMP_Settings.fallbackFontAssets != null)
                {
                    if (_regularFontAsset != null && !TMP_Settings.fallbackFontAssets.Contains(_regularFontAsset))
                    {
                        TMP_Settings.fallbackFontAssets.Insert(0, _regularFontAsset);
                    }
                    if (_boldFontAsset != null && _boldFontAsset != _regularFontAsset)
                    {
                        if (!TMP_Settings.fallbackFontAssets.Contains(_boldFontAsset))
                        {
                            TMP_Settings.fallbackFontAssets.Insert(0, _boldFontAsset);
                        }
                    }
                }

                // Optional: Direct text.font override
                if (_configOverrideDirectFont.Value)
                {
                    TextMeshProUGUI[] uis = Resources.FindObjectsOfTypeAll<TextMeshProUGUI>();
                    foreach (TextMeshProUGUI ui in uis)
                    {
                        if (ui != null && ui.font != _boldFontAsset && ui.font != _regularFontAsset)
                        {
                            ui.font = _regularFontAsset ?? _boldFontAsset;
                        }
                    }
                }

                if (modifiedCount > 0)
                {
                    Log.LogInfo("[UniversalFont] Successfully injected fallbacks into " + modifiedCount + " font tables.");
                }
            }
            catch (Exception ex)
            {
                Log.LogWarning("[UniversalFont] ApplyFontFallbacks error: " + ex.Message);
            }
        }
    }
}
