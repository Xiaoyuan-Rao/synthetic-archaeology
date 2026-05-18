"""
audio_driven_deformation.py
============================
Paste this into the **Callbacks DAT of a Script CHOP** in the
TouchDesigner network described in TOUCHDESIGNER_SETUP.md.

It reads the smoothed RMS from the upstream Math CHOP and writes four parameters
on the Noise SOP and Twist SOP inside the Geometry COMP that holds the imported
Blender fragment. The result is a fragment whose surface noise, spatial scale,
flowing Z-translation, and torsion all respond to the audio amplitude in real
time.

Author's note: this script is functionally identical in shape to the case study's
Turin audio script. The constants below were tuned by ear so the breathing is
strong on consonants but does not blow the mesh apart on the loudest peaks of
the TTS voice.
"""

# ---- TouchDesigner Script CHOP callback functions ----

def onCook(scriptOp):
    """Called every cook of the Script CHOP. The upstream Math CHOP feeds us
    one channel; its current value is the smoothed RMS of the voice signal."""
    scriptOp.clear()

    # ---- pull the RMS from the upstream Math CHOP ----
    inputs = scriptOp.inputs
    if not inputs:
        return
    rms = float(inputs[0][0])         # current sample of channel 0
    rms = max(0.0, min(1.5, rms))     # clamp to a safe driver range

    # ---- write the Noise SOP parameters ----
    geo  = op('geometry1')            # adjust if your Geometry COMP has a different name
    if geo is None:
        return
    noise = geo.op('noise1')
    twist = geo.op('twist1')
    if noise is None or twist is None:
        return

    # Noise amplitude — louder voice = surface trembles harder
    noise.par.amp = rms * 0.6

    # Noise period — louder voice = larger spatial wavelength
    noise.par.period = 0.5 + rms * 2.0

    # Noise translate Z — flowing over time so the deformation feels alive
    noise.par.tz = absTime.seconds * 0.2

    # Twist strength — torsion grows with the voice
    twist.par.strength = rms * 12.0

    # ---- echo the value back as a single-channel output (handy for debugging) ----
    out_chan = scriptOp.appendChan('rms_value')
    out_chan[0] = rms


def onPulse(par): pass

def onSetupParameters(scriptOp):
    """Optional: expose tunable constants on the Script CHOP itself,
    so they can be animated or driven by other CHOPs."""
    page = scriptOp.appendCustomPage('Driver')
    page.appendFloat('Noiseamp',    label='Noise Amplitude Gain', default=0.6)
    page.appendFloat('Noiseperiod', label='Noise Period Base',    default=0.5)
    page.appendFloat('Twiststr',    label='Twist Strength Gain',  default=12.0)
