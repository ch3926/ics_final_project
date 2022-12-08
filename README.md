# ics_final_project
 ICS final project - chat system

## ash
### encryption.py
#### general notes
* two classes: ENCRYPTION & CIPHER
#### encryption class
* general class/backbone for encryption
* generates private numbers, ppns, and public keys based off Diffie Hellman
* very basic incorporation of Diffie Hellman
#### cipher class
* generates codebook, uppercase and lowercase letter alphabet, scrambled
* encrypts based off amount of shift
* decrypts based off same shift

### notes on where it goes
* __client_state_machine.py__ -- in init, creates a random private number
* __GUI.py__ -- in the goAhead, calls get_ppn() in csm, generates PPN upon successful login & sends to server
* __client_state_machine.py__ -- method to generate PPN
* 
