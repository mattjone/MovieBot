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
      self.RecommendationStrings = ["I think you should check out %s! ", "This movie will blow your mind: %s. ", "Watch %s. It will ruin all other movies for you. "]

      self.ratedMovieList = {}
      self.userRatingVector = np.zeros(len(self.titles))
      self.recommendedMovies = []

      self.inTheMiddleOfSentimentAnalysis = False
      self.currentMovieForMoreInformation = ""
      self.check = {}
      self.distanceThreshold = 5
      self.confirm = False
      self.previousInput = ""


    def greeting(self):
      """chatbot greeting message"""

      HelloStrings = ["How can I help you?","Hey there! It's so nice to meet you.","What's up dude!"]
      GoodbyeStrings = ["Have a nice day!","I'm going to miss you.", "Am gonna be in my room crying until I see you again"]

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

      WrongFormatStrings = ["I'm sorry, is that the right format? Please make sure to include the name of the movie in quotation marks.","Whoaaa, can you please make sure you use quotation marks?","Quotation marks around the movie, buddy. Please and thank you."]
      UnknownMovieStrings = ["I'm sorry, I've never heard about that movie! Please tell me about another one.","Is that some random indie film? Never heard of it!","Man, I really need to get back to the cinema. Never heard of that movie..."]
      SameMovieStrings = ["Hey! You already told me about that movie. Tell me about a different one now.", "Come on man, pick a NEW movie!", "Have you only watched 1 movie in your entire life? Pick a new one, please"]
      ConfirmationStrings = ["I think you were talking about %s. Am I right?","It probably wouldn't hurt for you to brush up on your spelling a bit. Did you mean %s?","C'mon now, you can spell better than that! Were you talking about %s?"]
      ConfusedStrings = ["Hmmmm. Didn't quite get that one. Let's try again. Tell me about another movie!","Well this is going nowhere fast. From the top, lets try a new one!","Trying to keep me on my toes I see. How about we get back to some recommendations. Tell me about a movie you've seen!"]
      WhatIsStrings = ["To be honest, I'm not sure I'd like to talk about %s. How about we get back to movies?", "As much as I'd love to talk about %s, I'm really here for the movies. Give me another one!", "Would you rather chat about %s or get some movie recommendations? That what I thought. Hit me with a movie!"]
      CanYouStrings = ["I'm not big on talking about me. Lets focus on the movies.", "Can you?!? Back to the movies please.","I really appreciate how you've taken an interest in learning about me but all I really want to talk about is what you think about movies. How about one more?"]
      ArbitraryStrings = ["Ok, got it.", "Interesting. But not as interesting as movies. Let's get back to movie recommendations!","Wow you have such a broad range of interesting topics for discussion. I'd really like to stick to movies though.","Hmmmm very interesting. How about you let me know what you thought of another movie?"]

      if len(input) == 0:
          return "It seems you meant to say something but forgot"

      if len(self.recommendedMovies) > 0:
            movieRec = self.recommend(self.userRatingVector).title()
            response = random.choice(self.RecommendationStrings) % movieRec + " Tap any key to hear another recommendation. (Or enter :quit if you're done.)"
            return response

      if self.inTheMiddleOfSentimentAnalysis:
            self.inTheMiddleOfSentimentAnalysis = False
            response = self.addRating(self.currentMovieForMoreInformation, input)
            return response

      if self.confirm:
          self.confirm = False
          match = re.match("yep|yea|yes|y$|Yep|Yea|Yes|Y$",input)
          if match is None:
              return random.choice(ConfusedStrings)
          else:
              if self.currentMovieForMoreInformation in self.ratedMovieList:
                  return random.choice(SameMovieStrings)
              return self.addRating(self.currentMovieForMoreInformation, self.previousInput)

    #Explaining this regex - checks if there are articles, checks for the year, repeats it all twice
      match = re.match('.*\"(The|A|An|El|La)? *([\w ]*)( \(.*\)*)*\".*', input)
      if match is None:
          match = re.match('[^A-Z]*([A-Z].*)', input)
          if match is not None:
              matchSubstr = match.group(1).lower()
              splitSubStr = matchSubstr.split()
              movieName = ""
              for i in range(0,len(splitSubStr)):
                  movieName = movieName + " " + splitSubStr[i]
                  movieName = movieName.strip()
                  if movieName in self.titlesOnly:
                      input = self.removeTitle(movieName, input)
                      return self.addRating(movieName, input)
          if self.is_turbo:
              can_you = re.match("[Cc]an you (.*)", input)
              what_is = re.match("[Ww]hat is (.*)[\?.!]?", input)
              if can_you is not None:
                  return random.choice(CanYouStrings)
              if what_is is not None:
                  return random.choice(WhatIsStrings) % what_is.group(1)
              else:
                  return random.choice(ArbitraryStrings)
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
                movieName = self.findPotentialMovie(movieName)
                if movieName is None:
                    return random.choice(UnknownMovieStrings)
                else:
                    self.currentMovieForMoreInformation = movieName
                    self.confirm = True
                    self.previousInput = input
                    return random.choice(ConfirmationStrings) % movieName.title()


        else:
            response = random.choice(SameMovieStrings)
      else:
        response = random.choice(WrongFormatStrings)

      return response

    def addRating(self, movieName, string):
        rating = 0
        MoreMoviesStrings = ["Thank you! Please tell me about another movie.", "Whooo making progress. Give me another one.", "Just a few more movies and I will blow your mind with a recommendation. Give me one more."]
        NegationWords = ["didn't", "never", "not", "don't", "none", "not", "nobody"]

        strongPositive = ["love", "adore", "favorite", "amazing", "incredible", "fantastic"]
        strongNegative = ["awful", "terrible", "hate"]
        strongIntensifiers = ["really", "very", "extremely"]

        strongPositiveBoolean = False
        strongNegativeBoolean = False
        strongIntensifierBoolean = False

        ReverseBoolean = 1


        for word in string.split():
            if word in NegationWords:
                ReverseBoolean = -1
            if word in strongPositive:
                strongPositiveBoolean = True
            if word in strongNegative:
                strongNegativeBoolean = True
            if word in strongIntensifiers:
                strongIntensifierBoolean = True

            if self.p.stem(word) in self.sentiment:
                if self.sentiment[self.p.stem(word)] == "pos":
                    rating += (1 * ReverseBoolean)

                    if strongIntensifierBoolean:
                        strongPositiveBoolean = True
                        strongIntensifierBoolean = False
                else:
                    rating -= (1 * ReverseBoolean)

                    if strongIntensifiers:
                        strongNegativeBoolean = True
                        strongIntensifierBoolean = False
                ReverseBoolean = 1

        if rating >= 1:
            rating = 1
            strongNegativeBoolean = False
        elif rating < 0:
            rating = -1
            strongPositiveBoolean = False

        if rating == 0:
            self.inTheMiddleOfSentimentAnalysis = True
            self.currentMovieForMoreInformation = movieName
            response = movieName.title() + "! I didn't understand if you liked it or not. Tell me more."
            return response

        self.ratedMovieList[movieName] = rating
        self.userRatingVector[self.titlesOnly.index(movieName)] = rating

        if len(self.ratedMovieList) >= 5:
            movieRec = self.recommend(self.userRatingVector).title()
            response = random.choice(self.RecommendationStrings) % movieRec + " Tap any key to hear another recommendation. (Or enter :quit if you're done.)"
        else:
            if strongPositiveBoolean == True and strongNegativeBoolean == False:
                response = "Whoa, you really liked that one, huh? Give me another one. "
            elif strongNegativeBoolean == True and strongPositiveBoolean == False:
                response = "Wow, that bad, huh? Give me another one. "
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

    def minimumEditDistance(self,string, userInput, knownMovie):
        userLen = len(userInput)
        movieLen = len(knownMovie)
        concat = "%s %s" % (userInput , knownMovie)
        if userInput == knownMovie:
            return 0
        if userLen == 0:
            return movieLen
        elif movieLen == 0:
            return userLen
        if concat in self.check:
            return self.check[concat]
        else:
            x = min(self.minimumEditDistance("first",userInput[:-1],knownMovie)+1,
                      self.minimumEditDistance("second",knownMovie[:movieLen-1],userInput)+1,
                      self.minimumEditDistance("third",userInput[:userLen-1], knownMovie[:movieLen-1])+self.substitution(knownMovie[movieLen-1], userInput[userLen-1]))
            self.check[concat] = x
            return x

    def substitution(self, letterOne,letterTwo):
        if letterOne == letterTwo:
            return 0
        else:
            return 2

    def findPotentialMovie(self, string):
        start = time.time()
        minDist = None
        potentialMovie = None
        for i, title in enumerate(self.titlesOnly):
            if math.fabs(len(string) - len(title)) < 3:
                strSet = set(string)
                titleSet = set(title)
                if len(strSet - titleSet) > 2 or len(titleSet - strSet) > 2: continue
                self.check = {}
                dist = self.minimumEditDistance("zero",string, title)
                if (minDist is None or dist < minDist) and dist < self.distanceThreshold:
                    minDist = dist
                    potentialMovie = title
                    # print potentialMovie
                    # print minDist
        print time.time() - start, "edit distance time"
        return potentialMovie


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
      for movie_id, movie in enumerate(self.ratings):
          for user_id, rating in enumerate(movie):
            if rating != 0:
                self.ratings[movie_id,user_id] = 1 if rating > 2.5 else -1



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
    # print c.minimumEditDistance("test","sleping beauty","stealing beauty")
