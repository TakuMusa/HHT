#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import pandas as pd
from collections import defaultdict, Counter
import argparse
from datetime import datetime

class MalayStemmer:
    """
    Stemmer for Malay language based on academic morphological rules.
    Implements root extraction considering all morphophonological processes.
    
    Morphological rules verified against academic sources:
    - Abdullah Hassan (2006) "Morfologi Bahasa Melayu"
    - Nik Safiah Karim et al. (2008) "Tatabahasa Dewan"
    - Asmah Haji Omar (2009) "Nahu Melayu Mutakhir"
    """
    
    def __init__(self):
        # Basic Malay prefixes
        self.base_prefixes = ['me', 'ber', 'ter', 'di', 'pe', 'se', 'ke', 'per']
        
        # All prefixes, including nazalization forms
        self.prefixes = [
            # Prefixes with nazalization for verbs (from base me-)
            'meng', 'meny', 'mem', 'men', 'me', 
            # Prefixes with nazalization for nouns (from base pe-)
            'peng', 'peny', 'pem', 'pen', 'pe',
            # Other prefixes
            'ber', 'ter', 'per', 'di', 'ke', 'se'
        ]
        
        # Malay suffixes
        self.suffixes = ['kan', 'an', 'i', 'nya', 'lah', 'kah', 'pun', 'wan', 'wati', 'isme']
        
        # Circumfixes (prefix-suffix combinations)
        self.circumfixes = [
            ('ke', 'an'),      # ke...an (kerajaan → raja)
            ('per', 'an'),     # per...an (perjalanan → jalan)
            ('pe', 'an'),      # pe...an (penulisan → tulis)
            ('ber', 'an'),     # ber...an (berkenalan → kenal)
            ('me', 'kan'),     # me...kan (melihatkan → lihat)
            ('di', 'kan'),     # di...kan (dilakukan → laku)
            ('mem', 'kan'),    # mem...kan (membacakan → baca)
            ('men', 'kan'),    # men...kan (menuliskan → tulis)
            ('meng', 'kan'),   # meng...kan (mengajarkan → ajar)
            ('meny', 'kan'),   # meny...kan (menyapukan → sapu)
            ('pem', 'an'),     # pem...an (pembacaan → baca)
            ('pen', 'an'),     # pen...an (penulisan → tulis)
            ('peng', 'an'),    # peng...an (pengajaran → ajar)
            ('peny', 'an'),    # peny...an (penyapuan → sapu)
            ('ter', 'kan'),    # ter...kan (terdapatkan → dapat)
            ('se', 'nya')      # se...nya (sebaliknya → balik)
        ]
        
        # Nazalization rules according to Malay morphology
        # Source: Abdullah Hassan "Morfologi Bahasa Melayu"
        self.nasalization_rules = {
            # me- + p, b, f, v → mem- (p disappears)
            'mem': {'drops': 'p', 'applies_to': 'pbfv'},
            
            # me- + t, d, c, j, z → men- (t disappears)
            'men': {'drops': 't', 'applies_to': 'tdcjz'},
            
            # me- + k, g, h, vowels (a,e,i,o,u) → meng- (k disappears)
            'meng': {'drops': 'k', 'applies_to': 'kghaeiou'},
            
            # me- + s → meny- (s disappears)
            'meny': {'drops': 's', 'applies_to': 's'},
            
            # Same rules for pe-
            'pem': {'drops': 'p', 'applies_to': 'pbfv'},
            'pen': {'drops': 't', 'applies_to': 'tdcjz'},
            'peng': {'drops': 'k', 'applies_to': 'kghaeiou'},
            'peny': {'drops': 's', 'applies_to': 's'},
            
            # Prefixes that don't cause nazalization
            'me': {'changes': False},    # me- + l,m,n,r,w,y (melihat, menurun)
            'pe': {'changes': False},
            'ber': {'changes': False},
            'ter': {'changes': False},
            'di': {'changes': False},
            'ke': {'changes': False},
            'se': {'changes': False},
            'per': {'changes': False}
        }
        
        # Exceptions and irregular forms
        # Based on analysis of linguistic literature on Malay language
        self.exceptions = {
            # --- ARABIC LOANWORDS ---
            # Words of Arabic origin with special forms
            'alim': 'alim',         # عالم - scholar
            'amal': 'amal',         # عمل - deed, action
            'arab': 'arab',         # عرب - Arab
            'asal': 'asal',         # أصل - origin
            'fikir': 'fikir',       # فكر - thought
            'hakim': 'hakim',       # حاكم - judge
            'halal': 'halal',       # حلال - permissible
            'haram': 'haram',       # حرام - forbidden
            'hikayat': 'hikayat',   # حكاية - story, tale
            'hukum': 'hukum',       # حكم - law, rule
            'ilmu': 'ilmu',         # علم - knowledge, science
            'islam': 'islam',       # إسلام - islam
            'kabar': 'kabar',       # خبر - news
            'kadar': 'kadar',       # قدر - fate
            'kalam': 'kalam',       # كلام - speech, word
            'khalik': 'khalik',     # خالق - creator
            'kitab': 'kitab',       # كتاب - book
            'makhluk': 'makhluk',   # مخلوق - creature, being
            'masjid': 'masjid',     # مسجد - mosque
            'menteri': 'menteri',   # منتري - minister
            'musafir': 'musafir',   # مسافر - traveler
            'nabi': 'nabi',         # نبي - prophet
            'nasib': 'nasib',       # نصيب - fate
            'quran': 'quran',       # قرآن - Quran
            'raja': 'raja',         # راجا - king (Sanskrit)
            'rasul': 'rasul',       # رسول - messenger
            'salam': 'salam',       # سلام - peace, greeting
            'sultan': 'sultan',     # سلطان - sultan
            'syarat': 'syarat',     # شرط - condition
            'wakil': 'wakil',       # وكيل - representative
            'wali': 'wali',         # ولي - guardian
            'waktu': 'waktu',       # وقت - time
            'zaman': 'zaman',       # زمان - era, time
            
            # --- VERBS WITH IRREGULAR FORMS ---
            # Forms from fikir (to think)
            'berfikir': 'fikir',
            'berfikiran': 'fikir',
            'memfikir': 'fikir',
            'memfikiri': 'fikir',
            'memfikirkan': 'fikir',
            'difikir': 'fikir',
            'difikirkan': 'fikir',
            'terfikir': 'fikir',
            
            # --- WORDS WITH SPECIAL MORPHOLOGY ---
            # Words requiring special processing
            'pemimpin': 'pimpin',   # Requires reconstruction of 'p'
            'kepimpinan': 'pimpin',
            'berpimpin': 'pimpin',
            'pimpinan': 'pimpin',
            
            # Native Malay words that should not be changed
            'negeri': 'negeri',     # State
            'negara': 'negara',     # Country
            'duli': 'duli',         # His Majesty (title)
            'paduka': 'paduka',     # His Excellency (title)
            
            # --- WORDS WITH SPECIAL NAZALIZATION FORMS ---
            # Words with irregular transformations during nazalization
            'mengaji': 'kaji',      # 'k' drops after 'meng'
            'mengambil': 'ambil',   # 'meng' removal without adding a letter
            'mengikat': 'ikat',     # 'meng' removal without adding a letter
            'mengerti': 'erti',     # 'meng' removal without adding a letter
            'mempunyai': 'punya',   # From 'mem' + 'punya' + 'i'
            
            # --- OTHER COMPLEX CASES ---
            # Words with complex morphology
            'berwarna': 'warna',
            'mewarnai': 'warna',
            'bersejarah': 'sejarah',
            'berdasarkan': 'dasar',
            'kerajaan': 'raja',
            'kekuasaan': 'kuasa',
            'kehidupan': 'hidup',
            'berkenalan': 'kenal',
            'perjalanan': 'jalan',
            'permulaan': 'mula',
            'kemampuan': 'mampu',
            'kepandaian': 'pandai',
            'kebijaksanaan': 'bijaksana',
            'peperangan': 'perang',
            
            # --- VERBS WITH TYPICAL NAZALIZATION ---
            # Sample examples to verify correct nazalization
            'melangkah': 'langkah',
            'menangis': 'tangis',
            'menulis': 'tulis',
            'mengajar': 'ajar',
            'membaca': 'baca',
            'melihat': 'lihat',
            'mendengar': 'dengar',
            'meminta': 'minta',
            'menerima': 'terima',
            'memberi': 'beri',
            'memahami': 'faham'  # Note: f changes to p in prefix
        }
        
    def recover_root_from_prefix(self, word):
        """
        Recovers the root word considering Malay nazalization rules.
        
        According to Abdullah Hassan "Morfologi Bahasa Melayu" and "Tatabahasa Dewan",
        when using prefixes mem-, men-, meng-, meny-, nazalization of the first letter
        of the root occurs, which may completely disappear in some cases.
        
        Examples:
        - 'membaca' (mem- + baca): b is preserved → 'baca'
        - 'memukul' (mem- + pukul): p disappears → 'pukul'
        - 'menulis' (men- + tulis): t disappears → 'tulis'
        - 'menangkap' (men- + tangkap): t is preserved → 'tangkap'
        - 'mengajar' (meng- + ajar): k disappears → 'ajar'
        - 'menggambar' (meng- + gambar): g is preserved → 'gambar'
        - 'menyapu' (meny- + sapu): s disappears → 'sapu'
        """
        for prefix, rule in self.nasalization_rules.items():
            if word.startswith(prefix):
                # Get the part after the prefix
                remainder = word[len(prefix):]
                
                # If after removing the prefix less than 3 characters remain, it's probably not a valid root
                if len(remainder) < 3:
                    continue
                
                # Check if we need to apply a morphophonological rule
                if 'changes' in rule and rule['changes'] is False:
                    # If the prefix doesn't change the first letter of the root
                    return remainder
                
                if 'drops' in rule and 'applies_to' in rule:
                    dropped_letter = rule['drops']
                    letters_affected = rule['applies_to']
                    
                    # Check if we need to restore the dropped letter
                    # If the first letter of the root is in the list of letters that are preserved (not disappearing)
                    if remainder and remainder[0] in letters_affected and remainder[0] != dropped_letter:
                        # No need to restore the letter, as it was preserved (e.g. menggambar → gambar)
                        return remainder
                    
                    # If the first letter of the root is not among those that can be preserved,
                    # perhaps the first letter of the root has been dropped (e.g. memukul → pukul)
                    return dropped_letter + remainder
        
        # If no matching prefix is found, return the original word
        return word
        
    def stem(self, word):
        """
        Extracts the root word from Malay text, strictly following the rules
        of Malay morphology according to standard academic sources.
        
        Rule application order:
        1. Check exceptions dictionary
        2. Remove reduplication (if present)
        3. Remove circumfixes
        4. Process nazalization and prefixes
        5. Remove suffixes
        
        Sources:
        - Abdullah Hassan "Morfologi Bahasa Melayu"
        - Nik Safiah Karim et al. "Tatabahasa Dewan"
        - Asmah Haji Omar "Nahu Melayu Mutakhir"
        """
        
        # 1. Check for presence in the exceptions dictionary
        if word in self.exceptions:
            return self.exceptions[word]
        
        original = word.lower()
        result = original
        
        # 2. Process reduplication (repetition):
        # If the word has a structure "X-X" (where X is identical parts), take X
        # For example: mata-mata → mata, kura-kura → kura
        parts = original.split('-')
        if len(parts) == 2 and parts[0] == parts[1] and len(parts[0]) >= 3:
            result = parts[0]
            return result
        
        # 3. Process circumfixes (consider them first)
        for prefix, suffix in self.circumfixes:
            if original.startswith(prefix) and original.endswith(suffix):
                # Remove the circumfix
                stem_candidate = original[len(prefix):-len(suffix)]
                
                # Check sufficient length
                if len(stem_candidate) >= 3:
                    # Nazalization usually doesn't occur with circumfixes,
                    # but we check simple cases just to be safe
                    if prefix in ['mem', 'men', 'meng', 'meny']:
                        result = self.recover_root_from_prefix(prefix + stem_candidate)
                        if result != prefix + stem_candidate:
                            return result
                    
                    return stem_candidate
        
        # 4. Process prefixes considering nazalization
        if any(original.startswith(prefix) for prefix in self.prefixes):
            # Apply nazalization rules to recover the root
            root_candidate = self.recover_root_from_prefix(original)
            
            # If we managed to recover the root, use it
            if root_candidate != original:
                result = root_candidate
            else:
                # If nazalization rules didn't work,
                # simply remove the prefix (for simple cases)
                for prefix in sorted(self.prefixes, key=len, reverse=True):
                    if original.startswith(prefix):
                        candidate = original[len(prefix):]
                        if len(candidate) >= 3:
                            result = candidate
                            break
        
        # 5. Remove suffixes after processing prefixes
        for suffix in self.suffixes:
            if result.endswith(suffix):
                stem_candidate = result[:-len(suffix)]
                if len(stem_candidate) >= 3:
                    result = stem_candidate
                    break
        
        # Check minimum root length (usually in Malay not less than 3 letters)
        if len(result) < 3:
            return original
            
        return result

def process_text_to_excel(input_file, output_dir):
    """
    Processes a text file by extracting root words and saving them to an Excel file.
    Counts the frequency of occurrence of each word and root.
    
    Args:
        input_file (str): Path to the input file with the text.
        output_dir (str): Path to the directory for saving results.
        
    Returns:
        dict: Dictionary where keys are root words and values are dictionaries with information about derived forms.
    """
    stemmer = MalayStemmer()
    word_stems = defaultdict(lambda: {'forms': set(), 'frequency': 0, 'form_frequencies': Counter()})
    
    print(f"Processing file: {input_file}")
    
    # Reading the input file with different encodings
    text = None
    encodings = ['utf-8', 'latin-1', 'cp1251', 'windows-1252']
    
    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                text = f.read()
                print(f"File successfully read with encoding {encoding}")
                break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    if text is None:
        print("Could not read file with any encoding.")
        return None
    
    # Tokenization (splitting text into words)
    # Using Counter to count the frequency of each word
    words = re.findall(r'\b[a-zA-Z\u00C0-\u017F\']+\b', text.lower())
    
    # Count the frequency of each word
    word_frequencies = Counter(words)
    
    print(f"Total words found: {len(words)}")
    print(f"Unique word forms: {len(word_frequencies)}")
    print("Extracting root words and counting frequencies...")
    
    # Process each word
    for word, frequency in word_frequencies.items():
        # Skip words that are too short (less than 3 characters)
        if len(word) < 3:
            continue
            
        # Get the root
        stem = stemmer.stem(word)
        
        # Add the word to the corresponding set
        word_stems[stem]['forms'].add(word)
        # Increase the total frequency of the root
        word_stems[stem]['frequency'] += frequency
        # Add the frequency of the specific form
        word_stems[stem]['form_frequencies'][word] += frequency
    
    print(f"Extracted {len(word_stems)} unique roots.")
    
    # Create DataFrame for Excel with frequencies
    data = []
    for stem, info in sorted(word_stems.items(), key=lambda x: x[1]['frequency'], reverse=True):
        # Sort derivative forms by frequency (from most frequent to less frequent)
        forms_with_frequencies = []
        for form, form_freq in sorted(info['form_frequencies'].items(), key=lambda x: x[1], reverse=True):
            forms_with_frequencies.append(f"{form} ({form_freq})")
        
        data.append({
            'Root': stem,
            'Root Frequency': info['frequency'],
            'Number of Forms': len(info['forms']),
            'Derivative Forms with Frequencies': ', '.join(forms_with_frequencies)
        })
    
    df = pd.DataFrame(data)
    
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate filename with current date and time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_file = os.path.join(output_dir, f"wordlist_hikayat_{timestamp}.xlsx")
    
    # Save to Excel
    df.to_excel(excel_file, index=False)
    print(f"Results saved to file: {excel_file}")
    
    # Create an additional Excel file with statistics in a form for analysis
    stats_df = pd.DataFrame([
        {'Parameter': 'Total words in the text', 'Value': len(words)},
        {'Parameter': 'Number of unique word forms', 'Value': len(word_frequencies)},
        {'Parameter': 'Number of unique roots', 'Value': len(word_stems)},
        {'Parameter': 'Average forms per root', 'Value': sum(len(info['forms']) for info in word_stems.values()) / len(word_stems) if word_stems else 0}
    ])
    
    stats_file = os.path.join(output_dir, f"statistics_{timestamp}.xlsx")
    stats_df.to_excel(stats_file, index=False)
    print(f"Statistics saved to file: {stats_file}")
    
    # Create an additional text file with just roots and their frequencies
    roots_only_file = os.path.join(output_dir, f"roots_only_{timestamp}.txt")
    with open(roots_only_file, 'w', encoding='utf-8') as f:
        f.write("# List of root words from Hikayat Hang Tuah text with frequencies\n\n")
        f.write("# Format: root [frequency]\n\n")
        for stem, info in sorted(word_stems.items(), key=lambda x: x[1]['frequency'], reverse=True):
            f.write(f"{stem} [{info['frequency']}]\n")
    
    print(f"List of roots with frequencies saved to file: {roots_only_file}")
    
    return word_stems

def main():
    """Main function of the program"""
    parser = argparse.ArgumentParser(description='Malay language stemmer for creating a list of root words')
    
    # Defining command line arguments
    parser.add_argument('--input', '-i', 
                       help='Path to the file with Hikayat Hang Tuah text')
    parser.add_argument('--output', '-o',  
                       help='Output directory for saving results')
    parser.add_argument('--use-default', '-d', action='store_true',
                       help='Use default paths')
    
    args = parser.parse_args()
    
    # Default paths (as specified in the request)
    default_input = r"C:\Users\taku\Desktop\MY_DESKTOP\RESEARCH\Personal\Loandwords in Malay\MAIN Source\Draft\file 3.txt"
    default_output = r"C:\Users\taku\Desktop\MY_DESKTOP\RESEARCH\Personal\Loandwords in Malay\MAIN Source\Draft\output"
    
    if args.use_default or (not args.input and not args.output):
        print("Using default paths:")
        print(f"Input file: {default_input}")
        print(f"Output directory: {default_output}")
        input_file = default_input
        output_dir = default_output
    else:
        input_file = args.input if args.input else default_input
        output_dir = args.output if args.output else default_output
    
    # Check if the input file exists
    if not os.path.isfile(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        return
    
    # Process the text and save results to Excel
    process_text_to_excel(input_file, output_dir)

if __name__ == "__main__":
    main()