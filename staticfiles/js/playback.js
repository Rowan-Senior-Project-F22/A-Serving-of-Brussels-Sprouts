/**
 * -- SPOTIFY Web Playback Functionality --
 * 
 * Description: These functions are meant to support a simulated "synchronous" listening
 * session. The assumed preconditions are that an oAuth token should be injected via use
 * of the Django templating engine and the track ID should be known and provided by those
 * templates using the functions. The functions will take care of loading the
 * currently playing track on load and communicating thru use of the Spotify Web Playback
 * SDK.
 * 
 * @author chrisrinaldi
 * @date 3 December, 2022
 * @see https://developer.spotify.com/documentation/web-playback-sdk/quick-start/
 */


/**
 * Once the CDN for the Web Playback SDK has been loaded, initialize
 * the Spotify player.
 */
window.onSpotifyWebPlaybackSDKReady = () => {
    const token = '[My access token]';
    const player = new Spotify.Player({
      name: 'Web Playback SDK Quick Start Player',
      getOAuthToken: cb => { cb(token); },
      volume: 0.5
})};

// Ready
player.addListener('ready', ({ device_id }) => {
    console.log('Ready with Device ID', device_id);
});

  // Not Ready
player.addListener('not_ready', ({ device_id }) => {
    console.log('Device ID has gone offline', device_id);
});

player.addListener('initialization_error', ({ message }) => { 
    console.error(message);
});

player.addListener('authentication_error', ({ message }) => {
    // TODO: Add a fallback for re-retrieving auth token.
    console.error(message);
});

player.addListener('account_error', ({ message }) => {
    // TODO: Add a fallback for re-retrieving auth token.
    console.error(message);
});

player.connect();