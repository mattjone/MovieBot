#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PA6, CS124, Stanford, Winter 2016
# v.1.0.2
# Original Python code by Ignacio Cases (@cases)
# Ported to Java by Raghav Gupta (@rgupta93) and Jennifer Lu (@jenylu)
######################################################################
import csv
import math
import numpy as np
from movielens import ratings
from random import randint
from PorterStemmer import PorterStemmer
import re


class Chatbot:
    """Simple class to implement the chatbot for PA 6."""


    def __init__(self, is_turbo=False):
      self.name = 'moviebot'
      self.is_turbo = is_turbo
      self.p = PorterStemmer()
      self.read_data()
      self.ratedMovieList = {}

    def greeting(self):
      """chatbot greeting message"""
      greeting_message = 'How can I help you?'


      return greeting_message

    def goodbye(self):
      """chatbot goodbye message"""


      goodbye_message = 'Have a nice day!'



      return goodbye_message


    #############################################################################
    # 2. Modules 2 and 3: extraction and transformation                         #
    #############################################################################

    def process(self, input):
      """Takes the input string from the REPL and call delegated functions
      that
        1) extract the relevant information and
        2) transform the information into a response to the user
      """
      #############################################################################
      # TODO: Implement the extraction and transformation in this method, possibly#
      # calling other functions. Although modular code is not graded, it is       #
      # highly recommended                                                        #
      #############################################################################
      
      if re.match('.*\"(.*)\".*', input) is not None:
        movieName = re.match('.*\"(.*)\".*', input).group(1)
        
        if movieName not in self.ratedMovieList:
        
            if movieName in self.titlesOnly:
                rating = 0
            
                for word in input.split():
                    if self.p.stem(word) in self.sentiment:
                        if self.sentiment[self.p.stem(word)] == "pos":
                            rating += 1
                        else:
                            rating -= 1
                if rating >= 1:
                    rating = 1
                elif rating < 0:
                        rating = -1
        
                self.ratedMovieList[movieName] = rating
                
                
                if len(self.ratedMovieList) >= 5:
                    movieSet = self.recommend(self.ratedMovieList)
                    
                    response = "I recommend:"
                else:
                    response = "Thank you! Please tell me about another movie."
            else:
                response = "I'm sorry, I've never heard about that movie! Please tell me about another one."
        else:
            response = "Hey! You already told me about that movie. Tell me about a different one now."
      else:
        response = "I'm sorry, is that the right format? Please make sure the name of the movie is in quotation marks."

      return response


    #############################################################################
    # 3. Movie Recommendation helper functions                                  #
    #############################################################################

    def read_data(self):
      """Reads the ratings matrix from file"""
      # This matrix has the following shape: num_movies x num_users
      # The values stored in each row i and column j is the rating for
      # movie i by user j
      self.titles, self.ratings = ratings()
      reader = csv.reader(open('data/sentiment.txt', 'rb'))
      self.sentiment = dict(reader)
      
      self.titlesOnly = []
      
      for entry in self.titles:
            titleOnly = entry[0].split(' (')[0]
            self.titlesOnly.append(titleOnly)
      self.sentiment.update({self.p.stem(k): v for k, v in self.sentiment.items()})

    def binarize(self):
      """Modifies the ratings matrix to make all of the ratings binary"""

      pass


    def distance(self, u, v):
      """Calculates a given distance function between vectors u and v"""
      
      meanU = numpy.mean(u)
      meanV = numpy.mean(v)
      
      for elementU,elementV in u,v:
        numerator = numerator + ((elementU - meanU) * (elementV - meanV))
        sumU = sumU + (elementU - meanU)^2
        sumV = sumV + (elementV - meanV)^2
      
      denominator = sqrt(sumU) * sqrt(sumV)
      
      similarity = numerator/denominator

    def recommend(self, u):
      """Generates a list of movies based on the input vector u using
      collaborative filtering"""
      
      for
      

      pass


    def debug(self, input):
      """Returns debug information as a string for the input string from the REPL"""
      # Pass the debug information that you may think is important for your
      # evaluators
      debug_info = 'debug info'
      return debug_info


    #############################################################################
    # 5. Write a description for your chatbot here!                             #
    #############################################################################
    def intro(self):
      return """
      Your task is to implement the chatbot as detailed in the PA6 instructions.
      Remember: in the starter mode, movie names will come in quotation marks and
      expressions of sentiment will be simple!
      Write here the description for your own chatbot!
      """


    #############################################################################
    # Auxiliary methods for the chatbot.                                        #
    #                                                                           #
    # DO NOT CHANGE THE CODE BELOW!                                             #
    #                                                                           #
    #############################################################################

    def bot_name(self):
      return self.name


if __name__ == '__main__':
    Chatbot()
