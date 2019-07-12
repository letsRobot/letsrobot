# Google Cloud Text To Speech API
The Google Cloud TTS API offers high fidelity, ultra realistic speech synthesis. It has recently been made available for use on RemoTV by skeeter_mcbee. A demo is available on its website, https://cloud.google.com/text-to-speech.

This is not a free service. Prices may vary, but as of the time of this writing, a free one year trial is available with $300 credit towards all Google Cloud Platform services.

## Features
* Multilingual
    * Supports 30+ voices in 13 langues and variants
* WaveNet Voices
    * Exclusive multilingual access to DeepMind WaveNet voices that provide the most natural sounding speech.
* Text and SSML support
    * Customize your speech with SSML tags that allow you to add pauses, numbers, date and time formatting, and other pronounciation instructions.
* Speaking Rate Tuning
    * Customize your speaking rate to be 4x faster or slower than the normal rate.
* Pitch Tuning
    * Customize the pitch of your selected vioce, up to 20 semitones more or less than the default output.
* Volume Gain Control
    * Increase the volume of the output by up to 16db or decrease the volume up to -96db.
* Audio Format Flexibility
    * Choose from a number of audio formats including mp3, Linear16, Ogg Opus.
* Audio Profiles (BETA)
    * Optimize for the type of speaker from which your speech is intended to play, such as headphones or phone lines.

## Pricing
1. Standard (non-WaveNet) voices: up to 4 million characters free, then USD$4.00 per 1 million characters
2. WaveNet voices: Up to 1 million characters free, then USD$16.00 per 1 million characters.

# Setting up
## Before you begin
1. Select or create a [GCP project](https://console.cloud.google.com/cloud-resource-manager?_ga=2.9202677.-1786735001.1546386686).
2. Make sure that [billing](https://cloud.google.com/billing/docs/how-to/modify-project) is enabled for your project.
3. Enable the Cloud Text-to-Speech [API](https://console.cloud.google.com/flows/enableapi?apiid=texttospeech.googleapis.com&_ga=2.253124681.-1786735001.1546386686)
4. Set up authentication:
    1. In the GCP Console, go to the [Create service account key](https://console.cloud.google.com/apis/credentials/serviceaccountkey?_ga=2.244115397.-1786735001.1546386686) page.
    2. From the **Service Account** drop-down list, select **New service account**.
    3. Don't select a vlue from the **Role** drop-down list. No role is required to access this service.
    4. Click **Create**. A note appears, warning that this service account has no role.
    5. Click **Create without role**. A JSON file that contains your key downloads to your computer. (This needs to go onto your robot.)

Copy your JSON file to your robot. All of the following steps need to be run on your robot.

## Install the client library
```
python -m pip install --upgrade google-cloud-texttospeech
```

## Using it with the Robot
1. In controller.conf, set your tts `type` to `google_cloud`.
2. Choose a voice from [this list](https://cloud.google.com/text-to-speech/docs/voices). Make the following changes in the `[google_cloud]` section of `controller.conf `
    1. Set `key_file` to the full path of your key file. (i.e., `/home/pi/googlecloudkey.json`)
    2. Set `language_code` to the language code of the voice you want to use. It needs to match the one in the voice you use. (i.e., `en-US`)
    3. Set `voice` to the voice name of the voice you want to use. It needs to have a matching language code in the front. (i.e., `en-US-Wavenet-A`)

