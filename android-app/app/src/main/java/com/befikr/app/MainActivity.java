package com.befikr.app;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.telephony.PhoneNumberUtils;
import android.telephony.SmsManager;
import android.util.Log;
import android.webkit.GeolocationPermissions;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

public final class MainActivity extends Activity {
    private static final int SOS_PERMISSION_REQUEST = 4201;
    private static final int FILE_CHOOSER_REQUEST = 4202;
    private ValueCallback<Uri[]> pendingFileChooser;
    private WebView webView;
    private GeolocationPermissions.Callback pendingGeoCallback;
    private String pendingGeoOrigin;
    private PendingSos pendingSos;
    private boolean permissionRequestInProgress;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(0xFFF7F3EC);
        getWindow().setNavigationBarColor(0xFFF7F3EC);

        webView = new WebView(this);
        webView.setBackgroundColor(0xFFF7F3EC);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setGeolocationEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setDatabaseEnabled(true);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            settings.setSafeBrowsingEnabled(false);
        }

        webView.addJavascriptInterface(new BefikrBridge(), "BefikrAndroid");
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            @SuppressWarnings("deprecation")
            public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
                if (pendingFileChooser != null) pendingFileChooser.onReceiveValue(null);
                pendingFileChooser = callback;
                try {
                    Intent picker = params.createIntent();
                    picker.addCategory(Intent.CATEGORY_OPENABLE);
                    startActivityForResult(picker, FILE_CHOOSER_REQUEST);
                } catch (Exception exception) {
                    pendingFileChooser.onReceiveValue(null);
                    pendingFileChooser = null;
                    showToast("No file picker is available on this device.");
                }
                return true;
            }

            @Override
            public void onGeolocationPermissionsShowPrompt(String origin, GeolocationPermissions.Callback callback) {
                if (hasLocationPermission()) {
                    callback.invoke(origin, true, false);
                    return;
                }
                pendingGeoOrigin = origin;
                pendingGeoCallback = callback;
                requestRuntimePermissions(false);
            }
        });

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return routeUrl(request.getUrl());
            }

            @SuppressWarnings("deprecation")
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return routeUrl(Uri.parse(url));
            }

            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                WebResourceResponse resp = interceptAssetRequest(request.getUrl());
                if (resp != null) return resp;
                return super.shouldInterceptRequest(view, request);
            }

            @SuppressWarnings("deprecation")
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, String url) {
                WebResourceResponse resp = interceptAssetRequest(Uri.parse(url));
                if (resp != null) return resp;
                return super.shouldInterceptRequest(view, url);
            }

            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                Log.e("Befikr", "WebView error: " + description + " for " + failingUrl);
            }
        });

        setContentView(webView);
        webView.loadUrl(BuildConfig.BEFIKR_START_URL);
    }

    private WebResourceResponse interceptAssetRequest(Uri uri) {
        String host = uri.getHost();
        if (host == null) return null;

        boolean isAppHost = host.equalsIgnoreCase("befikr.app")
                || host.equalsIgnoreCase("befikr.local")
                || host.equalsIgnoreCase("10.0.2.2")
                || host.equalsIgnoreCase("localhost")
                || host.equalsIgnoreCase("127.0.0.1");

        if (!isAppHost) return null;

        String path = uri.getPath();
        if (path == null || path.isEmpty() || path.equals("/")) {
            path = "/index.html";
        }

        if (path.contains("?")) path = path.substring(0, path.indexOf("?"));
        if (path.contains("#")) path = path.substring(0, path.indexOf("#"));

        if (path.startsWith("/api/")) {
            return handleLocalApi(path, uri);
        }

        try {
            String assetPath = "web" + (path.startsWith("/") ? path : "/" + path);
            InputStream is = getAssets().open(assetPath);
            String mime = getMimeType(path);
            Map<String, String> headers = new HashMap<>();
            headers.put("Access-Control-Allow-Origin", "*");
            headers.put("Cache-Control", "no-cache");
            return new WebResourceResponse(mime, "UTF-8", 200, "OK", headers, is);
        } catch (IOException e) {
            // SPA fallback to index.html for unknown frontend routes
            try {
                InputStream is = getAssets().open("web/index.html");
                Map<String, String> headers = new HashMap<>();
                headers.put("Access-Control-Allow-Origin", "*");
                return new WebResourceResponse("text/html", "UTF-8", 200, "OK", headers, is);
            } catch (IOException ex) {
                return null;
            }
        }
    }

    private String getMimeType(String path) {
        String lower = path.toLowerCase();
        if (lower.endsWith(".html") || lower.endsWith(".htm")) return "text/html";
        if (lower.endsWith(".css")) return "text/css";
        if (lower.endsWith(".js") || lower.endsWith(".mjs")) return "application/javascript";
        if (lower.endsWith(".json") || lower.endsWith(".webmanifest")) return "application/json";
        if (lower.endsWith(".png")) return "image/png";
        if (lower.endsWith(".jpg") || lower.endsWith(".jpeg")) return "image/jpeg";
        if (lower.endsWith(".svg")) return "image/svg+xml";
        if (lower.endsWith(".ico")) return "image/x-icon";
        if (lower.endsWith(".mp3")) return "audio/mpeg";
        if (lower.endsWith(".wav")) return "audio/wav";
        if (lower.endsWith(".woff2")) return "font/woff2";
        if (lower.endsWith(".woff")) return "font/woff";
        if (lower.endsWith(".ttf")) return "font/ttf";
        return "application/octet-stream";
    }

    private WebResourceResponse handleLocalApi(String path, Uri uri) {
        String json = "{}";
        if (path.startsWith("/api/auth/")) {
            json = "{\"access_token\":\"offline_token_local\",\"token_type\":\"bearer\",\"user\":{\"id\":\"local_user_1\",\"name\":\"Befikr User\",\"email\":\"user@befikr.app\",\"role\":\"user\"}}";
        } else if (path.equals("/api/profile")) {
            json = "{\"id\":\"local_user_1\",\"name\":\"Befikr User\",\"email\":\"user@befikr.app\",\"role\":\"user\",\"created_at\":\"2026-11-15T00:00:00Z\"}";
        } else if (path.equals("/api/maps/config")) {
            json = "{\"provider\":\"offline_ai_decider\",\"offline\":true}";
        } else if (path.equals("/api/routes/data-status")) {
            json = "{\"state\":\"operational\",\"mapping_provider\":\"offline_ai_decider\",\"message\":\"Offline road network & synthetic safety dataset loaded locally on device.\",\"nirakshak_state\":\"local_csv\",\"safetipin_state\":\"local_csv\",\"data_gov_state\":\"local_csv\",\"dda_state\":\"local_csv\",\"google_places_state\":\"offline_csv\"}";
        } else if (path.equals("/api/contacts") || path.startsWith("/api/contacts/")) {
            json = "[]";
        } else if (path.equals("/api/voice/scripts") || path.equals("/api/scripts")) {
            json = "{\"scripts\":[]}";
        } else if (path.equals("/api/sos")) {
            json = "{\"id\":\"sos_local_1\",\"status\":\"created\",\"delivery_state\":\"local_only\",\"message\":\"SOS alert active on this device.\"}";
        } else if (path.equals("/api/places/autocomplete")) {
            try {
                String query = uri.getQueryParameter("input");
                if (query == null || query.trim().isEmpty()) {
                    query = uri.getQueryParameter("q");
                }
                String qLower = (query != null) ? query.trim().toLowerCase() : "";

                InputStream is = getAssets().open("web/data/offline_data.json");
                ByteArrayOutputStream baos = new ByteArrayOutputStream();
                byte[] buf = new byte[4096];
                int r;
                while ((r = is.read(buf)) != -1) baos.write(buf, 0, r);
                JSONObject dataObj = new JSONObject(baos.toString("UTF-8"));
                JSONArray places = dataObj.optJSONArray("places");
                JSONArray suggestions = new JSONArray();
                if (places != null && !qLower.isEmpty()) {
                    for (int i = 0; i < places.length(); i++) {
                        JSONObject p = places.getJSONObject(i);
                        String name = p.optString("name", "");
                        String address = p.optString("address", "");
                        String category = p.optString("category", "");

                        String haystack = (name + " " + address + " " + category).toLowerCase();
                        boolean matches = true;
                        String[] tokens = qLower.split("\\s+");
                        for (String token : tokens) {
                            if (!haystack.contains(token)) {
                                matches = false;
                                break;
                            }
                        }
                        if (!matches) continue;

                        JSONObject s = new JSONObject();
                        s.put("place_id", p.optString("id"));
                        s.put("name", name);
                        s.put("label", name);
                        s.put("address", address);
                        s.put("latitude", p.optDouble("latitude"));
                        s.put("longitude", p.optDouble("longitude"));
                        suggestions.put(s);
                        if (suggestions.length() >= 12) break;
                    }
                }
                JSONObject resp = new JSONObject();
                resp.put("suggestions", suggestions);
                resp.put("places", suggestions);
                resp.put("source", "offline_dataset");
                json = resp.toString();
            } catch (Exception e) {
                json = "{\"suggestions\":[],\"places\":[],\"source\":\"offline_data\"}";
            }
        } else if (path.equals("/api/places/resolve")) {
            try {
                InputStream is = getAssets().open("web/data/offline_data.json");
                ByteArrayOutputStream baos = new ByteArrayOutputStream();
                byte[] buf = new byte[4096];
                int r;
                while ((r = is.read(buf)) != -1) baos.write(buf, 0, r);
                JSONObject dataObj = new JSONObject(baos.toString("UTF-8"));
                JSONArray places = dataObj.optJSONArray("places");
                JSONObject chosen = (places != null && places.length() > 0) ? places.getJSONObject(0) : new JSONObject();
                JSONObject resp = new JSONObject();
                resp.put("place_id", chosen.optString("id", "off_1"));
                resp.put("latitude", chosen.optDouble("latitude", 28.6328));
                resp.put("longitude", chosen.optDouble("longitude", 77.2197));
                resp.put("address", chosen.optString("address", "Delhi"));
                resp.put("attributions", new JSONArray());
                json = resp.toString();
            } catch (Exception e) {
                json = "{\"place_id\":\"off_1\",\"latitude\":28.6328,\"longitude\":77.2197,\"address\":\"Delhi\",\"attributions\":[]}";
            }
        } else if (path.equals("/api/places/nearby")) {
            try {
                InputStream is = getAssets().open("web/data/offline_data.json");
                ByteArrayOutputStream baos = new ByteArrayOutputStream();
                byte[] buf = new byte[4096];
                int r;
                while ((r = is.read(buf)) != -1) baos.write(buf, 0, r);
                JSONObject dataObj = new JSONObject(baos.toString("UTF-8"));
                JSONArray places = dataObj.optJSONArray("places");
                JSONObject resp = new JSONObject();
                resp.put("places", places != null ? places : new JSONArray());
                resp.put("source", "offline_dataset");
                json = resp.toString();
            } catch (Exception e) {
                json = "{\"places\":[],\"source\":\"offline_data\"}";
            }
        } else if (path.startsWith("/api/routes/")) {
            try {
                String orig = uri.getQueryParameter("origin");
                String dest = uri.getQueryParameter("destination");
                String origLower = (orig != null) ? orig.trim().toLowerCase() : "";
                String destLower = (dest != null) ? dest.trim().toLowerCase() : "";

                InputStream is = getAssets().open("web/data/offline_data.json");
                ByteArrayOutputStream baos = new ByteArrayOutputStream();
                byte[] buf = new byte[4096];
                int r;
                while ((r = is.read(buf)) != -1) baos.write(buf, 0, r);
                JSONObject dataObj = new JSONObject(baos.toString("UTF-8"));
                JSONArray corridors = dataObj.optJSONArray("corridors");
                JSONObject matchedRes = null;
                if (corridors != null && corridors.length() > 0) {
                    for (int i = 0; i < corridors.length(); i++) {
                        JSONObject c = corridors.getJSONObject(i);
                        String cOrig = c.optString("origin", "").toLowerCase();
                        String cDest = c.optString("destination", "").toLowerCase();
                        if ((!origLower.isEmpty() && (cOrig.contains(origLower) || origLower.contains(cOrig))) &&
                            (!destLower.isEmpty() && (cDest.contains(destLower) || destLower.contains(cDest)))) {
                            matchedRes = c.optJSONObject("result");
                            break;
                        }
                    }
                    if (matchedRes == null) {
                        matchedRes = corridors.getJSONObject(0).optJSONObject("result");
                    }
                    if (matchedRes != null) {
                        json = matchedRes.toString();
                    } else {
                        json = corridors.getJSONObject(0).toString();
                    }
                } else {
                    json = "{\"routes\":[],\"state\":\"offline_ai_decider\"}";
                }
            } catch (Exception e) {
                json = "{\"routes\":[],\"state\":\"offline_data\"}";
            }
        } else {
            json = "{\"status\":\"ok\"}";
        }

        ByteArrayInputStream bais = new ByteArrayInputStream(json.getBytes(StandardCharsets.UTF_8));
        Map<String, String> headers = new HashMap<>();
        headers.put("Access-Control-Allow-Origin", "*");
        headers.put("Content-Type", "application/json");
        return new WebResourceResponse("application/json", "UTF-8", 200, "OK", headers, bais);
    }

    private boolean routeUrl(Uri uri) {
        String scheme = uri.getScheme() == null ? "" : uri.getScheme().toLowerCase();
        if (scheme.equals("tel")) {
            openDialer(uri);
            return true;
        }
        if (scheme.equals("https") || scheme.equals("http")) {
            Uri start = Uri.parse(BuildConfig.BEFIKR_START_URL);
            if (sameOrigin(uri, start)) return false;
            openExternal(uri);
            return true;
        }
        if (scheme.equals("mailto") || scheme.equals("sms")) {
            openExternal(uri);
            return true;
        }
        return true;
    }

    @Override
    @SuppressWarnings("deprecation")
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != FILE_CHOOSER_REQUEST || pendingFileChooser == null) return;
        ValueCallback<Uri[]> callback = pendingFileChooser;
        pendingFileChooser = null;
        Uri[] selected = WebChromeClient.FileChooserParams.parseResult(resultCode, data);
        java.util.ArrayList<Uri> allowed = new java.util.ArrayList<>();
        if (selected != null) for (Uri uri : selected) {
            if (uri != null && "content".equalsIgnoreCase(uri.getScheme())) allowed.add(uri);
        }
        callback.onReceiveValue(allowed.isEmpty() ? null : allowed.toArray(new Uri[0]));
    }

    @Override
    protected void onDestroy() {
        if (pendingFileChooser != null) {
            pendingFileChooser.onReceiveValue(null);
            pendingFileChooser = null;
        }
        super.onDestroy();
    }

    private boolean sameOrigin(Uri left, Uri right) {
        if (left.getHost() == null || right.getHost() == null) return false;
        if (left.getHost().equalsIgnoreCase(right.getHost())) return true;
        int leftPort = left.getPort() >= 0 ? left.getPort() : ("https".equalsIgnoreCase(left.getScheme()) ? 443 : 80);
        int rightPort = right.getPort() >= 0 ? right.getPort() : ("https".equalsIgnoreCase(right.getScheme()) ? 443 : 80);
        return left.getScheme().equalsIgnoreCase(right.getScheme())
                && left.getHost().equalsIgnoreCase(right.getHost())
                && leftPort == rightPort;
    }

    private void openDialer(Uri uri) {
        try {
            Intent intent = new Intent(Intent.ACTION_DIAL, uri);
            startActivity(intent);
        } catch (Exception exception) {
            showToast("No phone dialer is available on this device.");
        }
    }

    private void openExternal(Uri uri) {
        try {
            startActivity(new Intent(Intent.ACTION_VIEW, uri));
        } catch (Exception exception) {
            showToast("No app is available to open this link.");
        }
    }

    private boolean hasLocationPermission() {
        return checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                || checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED;
    }

    private boolean hasSmsPermission() {
        return checkSelfPermission(Manifest.permission.SEND_SMS) == PackageManager.PERMISSION_GRANTED;
    }

    private void requestRuntimePermissions(boolean includeSms) {
        if (permissionRequestInProgress) return;
        permissionRequestInProgress = true;
        String[] requested = includeSms
                ? new String[]{Manifest.permission.SEND_SMS, Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}
                : new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION};
        requestPermissions(requested, SOS_PERMISSION_REQUEST);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode != SOS_PERMISSION_REQUEST) return;
        permissionRequestInProgress = false;
        boolean locationGranted = hasLocationPermission();
        boolean smsGranted = hasSmsPermission();

        if (pendingGeoCallback != null) {
            pendingGeoCallback.invoke(pendingGeoOrigin, locationGranted, false);
            pendingGeoCallback = null;
            pendingGeoOrigin = null;
        }
        notifyWebPermissions(smsGranted, locationGranted);

        PendingSos queued = pendingSos;
        pendingSos = null;
        if (queued != null) {
            if (smsGranted) dispatchSosNow(queued);
            else {
                showToast("SMS permission was declined. Opening the 112 dialer.");
                openEmergencyDialer();
            }
        }
    }

    private void notifyWebPermissions(boolean smsGranted, boolean locationGranted) {
        if (webView == null) return;
        String script = "window.onBefikrAndroidPermissions && window.onBefikrAndroidPermissions({sms:"
                + smsGranted + ",location:" + locationGranted + "});";
        webView.post(() -> webView.evaluateJavascript(script, null));
    }

    private void dispatchSosNow(PendingSos sos) {
        int sentCount = 0;
        if (hasSmsPermission()) {
            try {
                JSONArray contacts = new JSONArray(sos.contactsJson);
                SmsManager smsManager = getSmsManager();
                java.util.HashSet<String> sentNumbers = new java.util.HashSet<>();
                for (int index = 0; index < contacts.length(); index++) {
                    JSONObject contact = contacts.optJSONObject(index);
                    if (contact == null) continue;
                    String number = normalizePhone(contact.optString("phone", ""));
                    if (number.isEmpty() || !sentNumbers.add(number)) continue;
                    smsManager.sendTextMessage(number, null, sos.message, null, null);
                    sentCount++;
                }
            } catch (Exception exception) {
                showToast("The SOS text could not be queued. Opening the 112 dialer.");
            }
        }

        if (sentCount > 0) {
            showToast("SOS text submitted for " + sentCount + " trusted contact" + (sentCount == 1 ? "." : "s."));
        } else if (hasSmsPermission()) {
            showToast("No trusted contact with a valid phone number was available. Opening the 112 dialer.");
        }
        openEmergencyDialer();
    }

    @SuppressWarnings("deprecation")
    private SmsManager getSmsManager() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            SmsManager manager = getSystemService(SmsManager.class);
            if (manager != null) return manager;
        }
        return SmsManager.getDefault();
    }

    private String normalizePhone(String input) {
        String number = PhoneNumberUtils.normalizeNumber(input == null ? "" : input.trim());
        if (number.isEmpty()) return "";
        if (number.startsWith("00")) number = "+" + number.substring(2);
        if (number.length() == 10) number = "+91" + number;
        else if (number.length() == 12 && number.startsWith("91")) number = "+" + number;
        else if (number.length() == 11 && number.startsWith("0")) number = "+91" + number.substring(1);
        if (number.length() < 10 || number.length() > 16) return "";
        return number;
    }

    private void openEmergencyDialer() {
        openDialer(Uri.parse("tel:112"));
    }

    private void showToast(String message) {
        runOnUiThread(() -> Toast.makeText(this, message, Toast.LENGTH_LONG).show());
    }

    @Override
    @SuppressWarnings("deprecation")
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }

    private final class BefikrBridge {
        @JavascriptInterface
        public boolean isAvailable() {
            return true;
        }

        @JavascriptInterface
        public boolean hasSosPermissions() {
            return hasSmsPermission() && hasLocationPermission();
        }

        @JavascriptInterface
        public void requestSosPermissions() {
            runOnUiThread(() -> {
                if (hasSmsPermission() && hasLocationPermission()) {
                    notifyWebPermissions(true, true);
                    showToast("SOS SMS and location permissions are ready.");
                } else {
                    requestRuntimePermissions(true);
                }
            });
        }

        @JavascriptInterface
        public void dispatchSos(String contactsJson, String message, String mapsUrl) {
            PendingSos sos = new PendingSos(contactsJson, message, mapsUrl);
            runOnUiThread(() -> {
                if (!hasSmsPermission()) {
                    pendingSos = sos;
                    requestRuntimePermissions(true);
                    return;
                }
                dispatchSosNow(sos);
            });
        }

        @JavascriptInterface
        public void openWhatsApp(String message) {
            runOnUiThread(() -> {
                Intent whatsapp = new Intent(Intent.ACTION_SEND);
                whatsapp.setType("text/plain");
                whatsapp.putExtra(Intent.EXTRA_TEXT, message == null ? "" : message);
                whatsapp.setPackage("com.whatsapp");
                try {
                    if (whatsapp.resolveActivity(getPackageManager()) != null) {
                        startActivity(whatsapp);
                    } else {
                        whatsapp.setPackage("com.whatsapp.w4b");
                        if (whatsapp.resolveActivity(getPackageManager()) != null) {
                            startActivity(whatsapp);
                        } else {
                            Intent chooser = new Intent(Intent.ACTION_SEND);
                            chooser.setType("text/plain");
                            chooser.putExtra(Intent.EXTRA_TEXT, message == null ? "" : message);
                            startActivity(Intent.createChooser(chooser, "Choose an app to share your SOS message"));
                        }
                    }
                } catch (Exception exception) {
                    showToast("WhatsApp is not available. Your SMS was handled separately.");
                }
            });
        }
    }

    private static final class PendingSos {
        final String contactsJson;
        final String message;
        final String mapsUrl;

        PendingSos(String contactsJson, String message, String mapsUrl) {
            this.contactsJson = contactsJson == null ? "[]" : contactsJson;
            this.message = message == null ? "SOS!!- Current location unavailable" : message;
            this.mapsUrl = mapsUrl;
        }
    }
}
