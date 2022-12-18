var redirect_uri = `${window.location.origin}/spotify_success`;


var access_token = null;
var refresh_token = null;
var display_name = null;
var email = null;
var currentPlaylist = "";
var radioButtons = [];

const AUTHORIZE = "https://accounts.spotify.com/authorize"
const TOKEN = "https://accounts.spotify.com/api/token";
const USERPROFILE = "https://api.spotify.com/v1/me";
const PLAYLISTS = "https://api.spotify.com/v1/me/playlists";
const DEVICES = "https://api.spotify.com/v1/me/player/devices";
const PLAY = "https://api.spotify.com/v1/me/player/play";
const PAUSE = "https://api.spotify.com/v1/me/player/pause";
const NEXT = "https://api.spotify.com/v1/me/player/next";
const PREVIOUS = "https://api.spotify.com/v1/me/player/previous";
const PLAYER = "https://api.spotify.com/v1/me/player";
const TRACKS = "https://api.spotify.com/v1/playlists/{{PlaylistId}}/tracks";
const CURRENTLYPLAYING = "https://api.spotify.com/v1/me/player/currently-playing";
const SHUFFLE = "https://api.spotify.com/v1/me/player/shuffle";

function onPageLoad() {
    client_id = localStorage.getItem("client_id");
    secret_id = localStorage.getItem("secret_id");
    if (window.location.search.length > 0 && !window.location.href.includes('/import_spotify')) {
        handleRedirect();
    }
}

function handleRedirect() {
    let code = getCode();
    fetchAccessToken(code);
    window.history.pushState("", "", redirect_uri); // remove param from url
}

function getCode() {
    let code = null;
    const queryString = window.location.search;
    if (queryString.length > 0) {
        const urlParams = new URLSearchParams(queryString);
        code = urlParams.get('code')
    }
    return code;
}

function fetchAccessToken(code) {
    let body = "grant_type=authorization_code";
    body += "&code=" + code;
    body += "&redirect_uri=" + encodeURI(redirect_uri);
    body += "&client_id=" + localStorage.getItem("client_id");
    body += "&secret_id=" + localStorage.getItem("secret_id");
    callAuthorizationApi(body);
}

function refreshAccessToken() {
    refresh_token = localStorage.getItem("refresh_token");
    let body = "grant_type=refresh_token";
    body += "&refresh_token=" + localStorage.getItem("refresh_token");
    body += "&client_id=" + localStorage.getItem("client_id");
    callAuthorizationApi(body);
}

function callAuthorizationApi(body) {
    let xhr = new XMLHttpRequest();
    xhr.open("POST", TOKEN, true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.setRequestHeader('Authorization', 'Basic ' + btoa(client_id + ":" + secret_id));
    xhr.send(body);
    xhr.onload = handleAuthorizationResponse;
}

function callApi(method, url, body, callback){
    let xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Authorization', 'Bearer ' + localStorage.getItem("access_token"));
    xhr.send(body);
    xhr.onload = callback;
}

function handleAuthorizationResponse() {
    if (this.status == 200) {
        var data = JSON.parse(this.responseText);
        console.log(data);
        var data = JSON.parse(this.responseText);
        if (data.access_token != undefined) {
            access_token = data.access_token;
            localStorage.setItem("access_token", access_token);
        }
        if (data.refresh_token != undefined) {
            refresh_token = data.refresh_token;
            localStorage.setItem("refresh_token", refresh_token);
        }
        onPageLoad();
    }
    else {
        console.log(this.responseText);
        alert(this.responseText);
    }
}

function requestAuthorization() {
    var client_id = "2de1575d99b14786ae4f7e46e33e494e";
    var secret_id = "fbf315776bda4ea2aaeeeb1ec559de7d";
    
    localStorage.setItem("client_id", client_id);
    localStorage.setItem("secret_id", secret_id); // In a real app you should not expose your secret_id to the user

    let url = AUTHORIZE;
    url += "?client_id=" + localStorage.getItem("client_id");
    url += "&response_type=code";
    url += "&redirect_uri=" + encodeURI(redirect_uri);
    url += "&show_dialog=true";
    url += "&scope=user-read-private user-read-email user-modify-playback-state user-read-playback-position user-library-read streaming user-read-playback-state user-read-recently-played playlist-read-private";
    window.location.href = url; // Show Spotify's authorization screen
}

function getUser(){
    callApi("GET", USERPROFILE, true, handleUserResponse); 
}

function handleUserResponse() {
    if (this.status == 200) {
        var data = JSON.parse(this.responseText);
        console.log(data);
        var data = JSON.parse(this.responseText);
        if (data.display_name != undefined) {
            display_name = data.display_name;
            localStorage.setItem("display_name", display_name);
        }
        if (data.email != undefined) {
            email = data.email;
            localStorage.setItem("email", email);
        }
        authenticateSpotifyUser();
    }
    else {
        console.log(this.responseText);
        alert(this.responseText);
    }  
}

function refreshDevices(){
    callApi( "GET", DEVICES, null, handleDevicesResponse );
}

function handleDevicesResponse(){
    if ( this.status == 200 ){
        var data = JSON.parse(this.responseText);
        console.log(data);
        removeAllItems( "devices" );
        data.devices.forEach(item => addDevice(item));
    }
    else if ( this.status == 401 ){
        refreshAccessToken()
    }
    else {
        console.log(this.responseText);
        alert(this.responseText);
    }
}

function addDevice(item){
    let node = document.createElement("option");
    node.value = item.id;
    node.innerHTML = item.name;
    document.getElementById("devices").appendChild(node); 
}


function deviceId(){
    return document.getElementById("devices").value;
}

function addDeviceWithName(){
    
}

function play(){
    let body = {};
    body.context_uri = "spotify:album:6mUdeDZCsExyJLMdAfDuwh";
    body.offset = {};
    body.offset.position = 0;
    body.offset.position_ms = 0;
    callApi( "PUT", PLAY + "?device_id=fa8cf59f057e6e8136d12b8c7e88269e0e38aa1a", JSON.stringify(body), handleApiResponse);
}

function request_playback() {
    let xhr = new XMLHttpRequest();
    let body = {}
    body.context_uri = "spotify:album:6mUdeDZCsExyJLMdAfDuwh";
    body.offset = {};
    body.offset.position = 0;
    body.offset.position_ms = 0;
    xhr.open("PUT", PLAY, true);
    xhr.setRequestHeader('Accept', 'application/json');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Authorization', 'Bearer '+ localStorage.getItem("access_token"));
    xhr.send(body);
    xhr.onload = handleApiResponse;
}

function handleApiResponse(){
    if ( this.status == 200){
        console.log(this.responseText);
        setTimeout(currentlyPlaying, 2000);
    }
    else if ( this.status == 204 ){
        setTimeout(currentlyPlaying, 2000);
    }
    else if ( this.status == 401 ){
        refreshAccessToken()
    }
    else {
        console.log(this.responseText);
        alert(this.responseText);
    }    
}

function authenticateSpotifyUser() {
    var email = localStorage.getItem("email");
    var username = localStorage.getItem("display_name").replace(/\s/g, "")
    var password           = '';
    var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for ( var i = 0; i < 12; i++ ) {
        password += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    let xhr = new XMLHttpRequest();
    let body = JSON.stringify({
        "username" : username,
        "email"    : email,
        "password" : password,
        "preferences" : "{'friends': 'Default', 'likes': [], 'dislikes': []}"
    });
    xhr.open("POST", 'spotify_success/landing_spotify/', true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.onload = function () {
        if (this.status >= 200 && this.status < 300) {
            window.location.href = `${window.location.origin}/landing/`;
            resolve(xhr.response);
        } else {
            // TODO: Handle an error.
            reject({
                status: this.status,
                statusText: xhr.statusText
            });
        }
    };
    xhr.onerror = function () {
        reject({
            status: this.status,
            statusText: xhr.statusText
        });
    };
    xhr.send(body);

}