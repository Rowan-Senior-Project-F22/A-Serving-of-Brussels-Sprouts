import { useState, useEffect } from "react"
import SpotifyPlayer from "react-spotify-web-playback"

export default function Player() {
    var accessToken = localStorage.getItem("access_token")
    const [play, setPlay] = useState(false)
    
    useEffect(() => setPlay(true), ['spotify:album:6mUdeDZCsExyJLMdAfDuwh'])
    
    if (!accessToken) return null
    return (
        <SpotifyPlayer
            token={accessToken}
            showSaveIcon
            callback={state => {
                if (!state.isPlaying) setPlay(false)
            }}
            play = {play}
            uris={ 'spotify:album:6mUdeDZCsExyJLMdAfDuwh' }
        />
    )
}