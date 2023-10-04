from pypdf import PdfReader
import spacy
import spacy_experimental
import re
import string
# import faulthandler

# faulthandler.enable()

def remove_punctuation(input_string):
    punctuation_regex = "(?<=[a-zA-Z])[.,;:!?\\-]"
    quotation_regex = "['\"]"
    input_string =  re.sub(punctuation_regex, "", input_string)
    input_string =  re.sub(quotation_regex, "", input_string)
    return input_string

def remove_extra_space_before_punc(input_string):
   input_string = input_string.replace(" !", "!")
   input_string = input_string.replace(" .", ".")
   input_string = input_string.replace(" ,", ",")
   input_string = input_string.replace(" ?", "?")
   input_string = input_string.replace(" :", ":")
   input_string = input_string.replace(" ;", ";")
   return input_string

def extract_paragraphs(page_text):
    # Replace needless dashes (might remove this later)
    page_text = page_text.replace(' - ', ', ')

    # Clean up text
    page_text_array = page_text.split('\n')
    page_text_array = [i.strip() for i in page_text_array]

    # Split page text into paragraphs and do some clean up
    paragraphs = []
    working_on_paragraph = False
    for item in page_text_array:
      if item == '':
          working_on_paragraph = False
      else:
          if working_on_paragraph:
            paragraphs[-1] += " {item}".format(item=item)
          else:
            paragraphs.append(item)
            working_on_paragraph = True
    
    return paragraphs
   
def clean_paragraphs(paragraphs, dictionary_words):
    formatted_paragraphs = []
    for paragraph in paragraphs:
      # Repair broken words and hyphenated words
      new_word_list = []
      words = paragraph.split()
      i = 0
      while i < len(words):
        if (i+1) < len(words):
          word_a = remove_punctuation(words[i]).lower()
          word_b = remove_punctuation(words[i+1]).lower()
          # Define booleans
          word_a_is_real = False
          word_b_is_real = False
          word_b_contains_hyphen = False
          words_combine_to_real = False

          # Check word A
          if word_a in dictionary_words:
              word_a_is_real = True

          # Check word B
          if word_b in dictionary_words:
              word_b_is_real = True
          elif '-' in words[i+1]:
              word_b_contains_hyphen = True

          # Checking combination of words
          if (word_a + word_b) in dictionary_words:
              words_combine_to_real = True
            
          if word_a_is_real and word_b_is_real:
              new_word_list.append(words[i])
              i += 1
          elif words_combine_to_real:
              new_word_list.append(words[i] + words[i+1])
              i += 2
          elif word_b_contains_hyphen:
              new_word_list.append(words[i] + words[i+1])
              i += 2
              if word_b[1:] not in dictionary_words:
                  print(word_b[1:])
          elif word_a_is_real:
              new_word_list.append(words[i])
              i += 1
          else:
              new_word_list.append(words[i])
              i += 1
              print(word_a)
        else:
            new_word_list.append(words[i])
            i += 1
      resolved_paragraph = remove_extra_space_before_punc(" ".join(new_word_list))
      formatted_paragraphs.append(resolved_paragraph)
        
    return formatted_paragraphs

def main():
    # Load in english dictionary
    dictionary_words = []
    f = open("dictionary.txt", "r")
    for x in f:
      dictionary_words.append(x.strip())

    # Load the small English pipeline
    nlp = spacy.load("en_core_web_sm")
    nlp_coref = spacy.load("en_coreference_web_trf")
    # doc = nlp_coref("The cats were startled by the dog as it growled at them.")
    # print(doc.spans)

    # return 0

    # extract the text
    pdf_name = "Arthur C. Clarke - The Odyssey Collection.pdf"
    if pdf_name is not None:
      pdf_reader = PdfReader(pdf_name)
      page_text = ""
      pages = pdf_reader.pages[33:42]
      for page in pages:
        page_text += page.extract_text()

      print(page_text)

      paragraphs = extract_paragraphs(page_text)

      processed_paragraphs = clean_paragraphs(paragraphs, dictionary_words)

      print(processed_paragraphs)
               

      for paragraph in processed_paragraphs:
         print('----------------------------')
         print(paragraph)
         print('----------------------------')
         
      processed_paragraphs_string = " ".join(processed_paragraphs)
      print(processed_paragraphs_string)

      doc = nlp_coref(processed_paragraphs_string)
      print(doc.spans)


      # # Process a text
      # doc = nlp(page_text)
      # # Iterate over the tokens
      # for token in doc:
      #     # Print the text and the predicted part-of-speech tag
      #     print(token.text, token.pos_, token.dep_, token.head.text)
      

if __name__ == '__main__':
    main()
