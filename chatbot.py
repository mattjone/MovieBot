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
import itertools as it
import time
import random


class Chatbot:
    """Simple class to implement the chatbot for PA 6."""


    def __init__(self, is_turbo=False):
      self.name = 'moviebot'
      self.is_turbo = is_turbo
      self.p = PorterStemmer()
      self.read_data()
    #   self.titles, self.ratings = ratings()
      self.binarize()
      self.recommendedMovies = []


    #############################################################################
    # 1. WARM UP REPL
    #############################################################################
      self.ratedMovieList = {}
      self.userRatingVector = np.zeros(len(self.titles))


    def greeting(self):
      """chatbot greeting message"""
      
      HelloStrings = ['How can I help you?']
      GoodbyeStrings = ['Have a nice day!']
      
      greeting_message = random.choice(HelloStrings)


      return greeting_message

    def goodbye(self):
      """chatbot goodbye message"""


      goodbye_message = random.choice(GoodbyeStrings)



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
      
     WrongFormatStrings = ["I'm sorry, is that the right format? Please make sure to include the name of the movie in quotation marks."]
     UnknownMovieStrings = ["I'm sorry, I've never heard about that movie! Please tell me about another one."]
     SameMovieStrings = ["Hey! You already told me about that movie. Tell me about a different one now."]
     MoreMoviesStrings = ["Thank you! Please tell me about another movie."]
     RecommendationStrings = ["I think you should check out %s!"]
    
    
      if len(input) == 0:
          return "It seems you meant to say something but forgot"
      match = re.match('.*\"(The|A|An|El|La)* *([\w ]*)( \(.*\)*)*\".*', input)
      if match is None:
          match = re.match('.*([A-Z].*)', input)
          if match is not None:
              matchSubstr = match.group(1).lower()
              splitSubStr = matchSubstr.split()
              movieName = ""
              for i in range(0,len(splitSubStr)):
                  movieName = movieName + " " + splitSubStr[i]
                  movieName = movieName.strip()
                  print movieName
                  if movieName in self.titlesOnly:
                      input = self.removeTitle(movieName, input)
                      return self.addRating(movieName, input)

          return random.choice(WrongFormatStrings)

      if match is not None:
        if match.group(1):
            movieName = match.group(2) + ", " + match.group(1)
        else:
            movieName = match.group(2)
        movieName = movieName.lower()
        if movieName not in self.ratedMovieList:

            if movieName in self.titlesOnly:
                input = self.removeTitle(movieName, input)
                return self.addRating(movieName, input)
            else:
                response = random.choice(UnknownMovieStrings)
        else:
            response = random.choice(SameMovieStrings)
      else:
        response = random.choice(WrongFormatStrings)

      return response

    def addRating(self, movieName, string):
        rating = 0

        for word in string.split():
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
        self.userRatingVector[self.titlesOnly.index(movieName)] = rating

        if len(self.ratedMovieList) >= 5:
            movieRec = self.recommend(self.userRatingVector).title()
            response = random.choice(RecommendationStrings) % movieRec
        else:
            response = random.choice(MoreMoviesStrings)
        return response

    def removeTitle(self, movieName, input):
        movieSplit = movieName.split()
        inputSplit = input.lower().split()
        for word in movieSplit: #remove the movie title from the words
            if word in inputSplit: inputSplit.remove(word)
        input = " ".join(inputSplit)
        return input


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
            self.titlesOnly.append(titleOnly.lower())
      self.sentiment.update({self.p.stem(k): v for k, v in self.sentiment.items()})

    def binarize(self):
      """Modifies the ratings matrix to make all of the ratings binary"""
      total = 0
      count = 0
      avg_rating = 0
      for movie in self.ratings:
          for rating in movie:
            if rating != 0:
                  total += rating
                  count += 1
      avg_rating = total / count
      for movie_id, movie in enumerate(self.ratings):
          for user_id, rating in enumerate(movie):
            if rating != 0:
                self.ratings[movie_id,user_id] = 1 if rating > avg_rating else -1



    def distance(self, u, v):
      """Calculates a given distance function between vectors u and v"""
      numerator = np.dot(u,v)
      denominator = np.linalg.norm(u) * np.linalg.norm(v)
      similarity = numerator/(denominator +1e-7)
      return similarity

    def recommend(self, u):
      """Generates a list of movies based on the input vector u using
      collaborative filtering"""
    #   print(u)
    #   print(len(u))
    #   exit()
      sims = {} #similarities
      recommendation = ""
      topScore = None
      start = time.time()
      for movie_id, rating in enumerate(u):
          if rating != 0:
              sims[movie_id] = {}
              for r_id, movie in enumerate(self.ratings):
                  sims[movie_id][r_id] = self.distance(movie,self.ratings[movie_id])
    #   print time.time() - start, "distance time"

      start = time.time()
      for i, movieRating in enumerate(self.ratings):
          iPrediction = 0
          for movieName in self.ratedMovieList:
              j = self.titlesOnly.index(movieName)
            #   sims[j][i]*1.0
            #   print("movies are %s and %s" % (self.titlesOnly[i], movieName))
            #   print("similarity between %s and %s is %.5f" % (self.titlesOnly[i], movieName, sims[j][i]))
              iPrediction += sims[j][i]*1.0 * self.userRatingVector[j]
            #   print("sims[j][i] is %.5f" % sims[j][i])
            #   print("self.userRatingVector[j]*1.0 is %d" % self.userRatingVector[j])
            #   print("iPrediction is %.5f" % iPrediction)
          if topScore is None or iPrediction > topScore:
              movie = self.titlesOnly[i]
              if movie not in self.ratedMovieList and movie not in self.recommendedMovies:
                #   print("prediction score for %s is %.5f" % (movie, iPrediction))
                  topScore = iPrediction
                  recommendation = movie
    #   print time.time() - start, "recommendation time"
      self.recommendedMovies.append(recommendation)
      return recommendation



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
