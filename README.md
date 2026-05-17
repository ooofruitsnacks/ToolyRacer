# ToolyRacer
### Simple retro racing game optimized for the RP2040 and the Tufty 2040 written in micropython :)

@ooofruitsnacks on codeberg and tangled / SOURCE CODE WILL BE ADDED TO TANGLED SOON, CODEBERG ADDED 05.17.26.
_____
### REQUIREMENTS 
- thonny installed on your computer  ( link https://thonny.org )
- TUFTY 2040
- RP2040 micropython flash ( link https://github.com/pimoroni/pimoroni-pico/releases ) go to "GETTING STARTED" to verify correct ver. 
- Pimoroni QwSTPad (optional easier controls)
_____

<img width="5712" height="4284" alt="image00001" src="https://github.com/user-attachments/assets/b252e133-5920-4f63-84cd-51034cf799c2" />

<img width="3558" height="2668" alt="image00003" src="https://github.com/user-attachments/assets/ffefa459-2845-4c0a-8342-7dd032d782b1" />

<img width="5712" height="4284" alt="image00002" src="https://github.com/user-attachments/assets/b7fc7eb9-f38d-4455-a8ce-4e6bff96bb58" />

https://github.com/user-attachments/assets/64a02b4d-bd5f-4f9a-b41f-02e73fedb86b

# GETTING STARTED
How to verify correct ver. for micrpython flash 
 download this version "tufty2040-v1.27.0-pimoroni-micropython.uf2"
- https://github.com/pimoroni/pimoroni-pico/releases
<img width="1048" height="80" alt="Screenshot 2026-05-09 at 10 37 55 PM" src="https://github.com/user-attachments/assets/14db645b-4abf-43ac-8c11-b4e8a5c8c922" />

-

Once the micropython flash has been downloaded to your computer, open thonny on your computer. 
<img width="1154" height="672" alt="Screenshot 2026-05-05 at 8 56 55 PM" src="https://github.com/user-attachments/assets/c0b1397d-9513-44f2-9614-26c517c805f7" />

Now click at the top of the screen in "Tools" and then click "Options" or at the bottom right hand corner of the screen.
    
<img width="356" height="262" alt="Screenshot 2026-05-05 at 9 04 19 PM" src="https://github.com/user-attachments/assets/6d417290-c5e6-4dcb-b000-c9e830ba1aa5" />

<img width="457" height="175" alt="Screenshot 2026-05-05 at 9 04 03 PM" src="https://github.com/user-attachments/assets/68dfc4e2-cc7b-4065-9042-38c7dd74b03c" />

Now click the interpreter tab, if micropython (RP2040) isn't already selected, scroll down to select micropython (RP2040).
   
<img width="742" height="614" alt="Screenshot 2026-05-05 at 9 05 08 PM" src="https://github.com/user-attachments/assets/bb746f13-27d5-4380-8e5f-8276b3b9c7cf" />

<img width="739" height="608" alt="Screenshot 2026-05-05 at 9 05 18 PM" src="https://github.com/user-attachments/assets/74dc615a-fe40-4b82-aa30-4d981d92717d" />

<img width="743" height="603" alt="Screenshot 2026-05-05 at 9 05 28 PM" src="https://github.com/user-attachments/assets/1c222b22-fb53-4e7b-a127-8c599eb1c972" />

- Make sure all power is off from the Tufty 2040, the battery turned to the off position as well.
- Plug the Tufty 2040 in via USBC into your computer. Turn on the Tufty 2040 and hold the usr/boot button for a few seconds to sync to your computer.
- At the top of Thonny, select "view" and then select "files". It should list all your files/folders on your computer and RP2040/Tufty2040 to the left of your commands and shell section.
# 2 options for QwSTPad setup (Almost done I swear!!)
### Option 1 
Find the folder on your computer named "QwSTPad-micropython-main" and then go to the src folder and you should see the "qwstpad.py". Right click on the file and click the option "upload to /". This will upload the QwSTPad flash to the RP2040 to read, recongize and communicate between your devices.

<img width="258" height="115" alt="Screenshot 2026-05-09 at 10 31 52 PM" src="https://github.com/user-attachments/assets/bbfe2b81-d28f-48ab-b15d-d4f1c732a403" />


ex: of where to find files
If you don't care how it will look on this device, this will work fine. Notice how it says qwstpad on the list of games even though it's not? This can be fixed easily with option 2.
<img width="5712" height="4284" alt="IMG_1528" src="https://github.com/user-attachments/assets/a8e35fe6-e199-4102-867a-621eda40fdec" />

### Option 2
Create a directory to store the qwstpad flash. This can be done by viewing the files on your computer, right clicking on "QwSTPad-micropython-main" and select new directory. save it to your RP2040 and it will save all the files without displaying them. 
<img width="309" height="207" alt="Screenshot 2026-05-09 at 11 22 42 PM" src="https://github.com/user-attachments/assets/d282f6ae-17a0-42ce-a76f-c78f3e685af6" />
<img width="4048" height="3036" alt="IMG_1527" src="https://github.com/user-attachments/assets/5c7aa229-622e-4314-8be8-20b3a05d99e0" />

yayyyy all cleaned up and all finished.

# MAKE A COPY OF SOURCE CODE TO EDIT FOR YOURSELF
MAKE A NEW DOCUMENT WITHIN THONNY AND OPEN THE SOURCE CODE

<img width="349" height="208" alt="Screenshot 2026-05-05 at 9 28 21 PM" src="https://github.com/user-attachments/assets/97ceea88-6949-430f-a80e-9b4faff6ed78" />

CHANGE, EDIT, TEST, AND EXPLORE!
<img width="1134" height="616" alt="Screenshot 2026-05-05 at 9 29 49 PM" src="https://github.com/user-attachments/assets/27f14f6a-6d35-404b-869a-cb42edaf9b6a" />

YOU CAN CHANGE YOUR CAR DIMENSIONS AND GAME SETTINGS WITH THESE LINES.
<img width="792" height="347" alt="Screenshot 2026-05-05 at 9 46 15 PM" src="https://github.com/user-attachments/assets/c44e8fb6-2644-4d34-89cd-4b3840056b61" />

ON LINE 105, YOU CAN ADD OR REMOVE COLORS IN THE [ ] TO CHANGE TRAFFIC COLOR WITH THESE COLORS 
<img width="713" height="202" alt="Screenshot 2026-05-05 at 9 46 26 PM" src="https://github.com/user-attachments/assets/c1cdddec-2cc2-4536-99bf-f88601917e07" />
