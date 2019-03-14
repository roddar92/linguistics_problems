## Computational linguistics

Welcome to the main page of my project! This repository stores examples of linguistics problems.

My name is Daria, I'm a software engineer with skills in natural language processing. My general scientific interests are knowledge bases and facts extraction. There are very important analysis tools that provides semantic analysis and text mining.

Project has next sections:
* [Pre-morphology](#pre-morphology)
* [Phonology](#phonology)
* [Morphology](#morphology)
* [Knowledge engineering](#knowledge-engineering)
* [N-grams applications](#n-grams-applications)
* [Games](#games)

In the source code three languages is supported now: English, Russian and Finnish. I hope that very soon next publishing problems will implement NLP-algorithms for more languages.

Source code:

#### Pre-morphology
- [Russian tokenizer](src/russian/NaiveTokenizer.py)
- [Sentence boundary detection](src/russian/NaiveSentenceBoundaryDetector.py)
- [Transliteration Russian <=> Latin (with spell-checker)](src/russian/NaiveTransliterator.py)
- [Word decomposition](src/russian/WordDecompounder.py)
- [Camel case segmentator](src/english/CamelCaseSplitter.py)
- [Distance to anagram](src/english/Anagrams.py)
- [Russian number2text converter](src/russian/TextNormalizer.py)

#### Phonology
- [Soundex Algorithm Implementation](src/russian/Soundex.py)
- [Syllable Module (word syllables count (russian/english/finnish) and word syllables list (russian/finnish))](src/russian/Syllables.py)

#### Morphology
- [Russian patronymic generator](src/russian/Patronymic-ya.py)
- [Russian diminutive names generator](src/russian/Diminutive_Names.py)
- [Russian cases generator (dative)](src/russian/Russian_Caser.py)
- [Russian cognate words checker](src/russian/Cognate_Words.py)
- [English Adjective Comparisoner](src/english/Comparative_or_Superlative.py)
- [Common English question generator](src/english/Question.py)
- [Finnish Predicative Sentences](src/suomi/FinnishPredicativeQuestioner.py)
- [Russian POS-tagger](src/russian/NaivePosTagger.py)

#### Syntax
- [Syntax analyzer for simple sentences](src/russian/NaiveSyntaxAnalyzer.py)

#### Knowledge engineering
- [Family tree](src/ontologies/Pedigree.py)
- [Abstract ontology for company](src/ontologies/CompanyOntology.py)
- [Simple timetable QA-system](src/ontologies/Timetable.py)
- [Bookshelf](src/ontologies/biblio)

#### N-grams applications
- [N-gram dictionary (for spelling/for language modeling)](src/ngrams/NGramDictionaryManager.py)
- [N-gram language model](src/ngrams/LanguageModel.py)
- [Collocations](src/ngrams/Collocations.py)
- [Russian diminutive names generator with RNN](src/ngrams/Diminutive-rnn.py)
- [Russian character RNN (non-smoothing)](src/ngrams/CharLevelLanguageModel.py)
- [Russian joking language model (PI Day)](src/ngrams/PiDayLanguageModel.py)
- [Simple spell-checker (based on n-grams and Damerau-Levenstein distance)](src/russian/SpellChecker.py)
- Advanced spell-checker based on:
    - dictionary of words from good texts with 2-3-gram index;
    - train language model with 2-grams on good texts;
    - retrieval `candidates` with Damerau-Levenstein distance;
    - find `candidate` with max probability of bigram `max{ P(prev_word, candidate), candidate in candidates}`

#### Games
 - [Russian Cities](src/russian/games/Cities.py)
 - [Guess City](src/russian/games/Guess_City.py)
 - [Guess Number](src/russian/games/More_or_Less.py)
 - [Secret Letter](src/russian/games/Secret_Letter.py)
 - [Opposites](src/russian/games/Opposites_Game.py)