#! bin/bash

systemctl --user disable mountToServers
systemctl --user disable takeMeToBigBird

cp ~/Desktop/timp/fastq-automation/src/systemdServiceFiles/mountToServers.service ~/.config/systemd/user/mountToServers.service
cp ~/Desktop/timp/fastq-automation/src/systemdServiceFiles/takeMeToBigBird.service ~/.config/systemd/user/takeMeToBigBird.service

systemctl --user daemon-reload

systemctl --user enable mountToServers
systemctl --user enable takeMeToBigBird
