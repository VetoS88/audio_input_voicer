# Script for voice input text over yandex speechkit

Disable middle button mouse
```bash
xmodmap -e "pointer = 1 25 3 4 5 6 7 8 9"
```

Add yandex speech kit key in settings.py file
```python
yandex_secret = "secret"
```

Run script

```bash
python run_voicer2.py
```

## Available modes
- Full phrase  
Start input by hold middle mouse button
- Continue  
Press shift then hold middle mouse button
- Replace   
Highlight phrase and press shift then hold middle mouse button




## ruff check
```bash
ruff check --fix
```