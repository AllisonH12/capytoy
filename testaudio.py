import pyaudio
print("starting")
p = pyaudio.PyAudio()
print("step1")


for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(info['index'], info['name'], info['defaultSampleRate'])
p.terminate()
