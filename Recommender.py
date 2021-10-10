import implicit
import numpy as np
import scipy
from scipy.sparse import csr_matrix

emoji_scores = {
    '\xf0\x9f\x98\x80' : 0.1,
    '\xf0\x9f\x98\x83' : 0.3,
    '\xf0\x9f\x98\x84' : 0.7,
    '\xf0\x9f\x98\x81' : 0.75,
    '\xf0\x9f\x98\x86' : 0.6,
    '\xf0\x9f\x98\x85' : 0.05,
    '\xf0\x9f\x98\x82' : 0.68,
    '\xf0\x9f\xa4\xa3' : 0.72,
    '\xf0\x9f\xa5\xb2' : -0.6,
    '\xe2\x98\xba\xef\xb8\x8f' : 0.56,
    '\xf0\x9f\x98\x8a' : 0.6,
    '\xf0\x9f\x98\x87' : 0.45,
    '\xf0\x9f\x99\x82' : 0.37,
    '\xf0\x9f\x99\x83' : 0.15,
    '\xf0\x9f\x98\x89' : 0.17,
    '\xf0\x9f\x98\x8c' : 0.56,
    '\xf0\x9f\x98\x8d' : 0.85,
    '\xf0\x9f\xa5\xb0' : 0.93,
    '\xf0\x9f\x98\x98' : 0.55,
    '\xf0\x9f\x98\x97' : 0.3,
    '\xf0\x9f\x98\x99' : 0.36,
    '\xf0\x9f\x98\x9a' : 0.42,
    '\xf0\x9f\x98\x8b' : 0.05,
    '\xf0\x9f\x98\x9b' : -0.1,
    '\xf0\x9f\x98\x9d' : -0.3,
    '\xf0\x9f\x98\x9c' : -0.01,
    '\xf0\x9f\xa4\xaa' : -0.03,
    '\xf0\x9f\xa4\xa8' : -0.45,
    '\xf0\x9f\xa7\x90' : 0.03,
    '\xf0\x9f\xa4\x93' : 0.02,
    '\xf0\x9f\x98\x8e' : 0.54,
    '\xf0\x9f\xa5\xb8' : -0.05,
    '\xf0\x9f\xa4\xa9' : 0.89,
    '\xf0\x9f\xa5\xb3' : 0.87,
    '\xf0\x9f\x98\x8f' : 0.23,
    '\xf0\x9f\x98\x92' : -0.46,
    '\xf0\x9f\x98\x9e' : -0.6,
    '\xf0\x9f\x98\x94' : -0.65,
    '\xf0\x9f\x98\x9f' : -0.35,
    '\xf0\x9f\x98\x95' : -0.33,
    '\xf0\x9f\x99\x81' : -0.63,
    '\xe2\x98\xb9\xef\xb8\x8f' : -0.76,
    '\xf0\x9f\x98\xa3' : -0.58,
    '\xf0\x9f\x98\x96' : -.46,
    '\xf0\x9f\x98\xab' : 0.15,
    '\xf0\x9f\x98\xa9' : 0.35,
    '\xf0\x9f\xa5\xba' : 0.7,
    '\xf0\x9f\x98\xa2' : -0.87,
    '\xf0\x9f\x98\xad' : -0.98,
    '\xf0\x9f\x98\xa4' : 0.03,
    '\xf0\x9f\x98\xa0' : -0.2,
    '\xf0\x9f\x98\xa1' : -0.5,
    '\xf0\x9f\xa4\xac' : -0.95,
    '\xf0\x9f\xa4\xaf' : 0.6,
    '\xf0\x9f\x98\xb3' : -0.15,
    '\xf0\x9f\xa5\xb5' : 0.1,
    '\xf0\x9f\xa5\xb6' : -0.1,
    '\xf0\x9f\x98\xb6\xe2\x80\x8d\xf0\x9f\x8c\xab\xef\xb8\x8f' : -0.05,
    '\xf0\x9f\x98\xb1' : -0.76,
    '\xf0\x9f\x98\xa8' : -0.48,
    '\xf0\x9f\x98\xb0' : -0.8,
    '\xf0\x9f\x98\xa5' : -0.87,
    '\xf0\x9f\x98\x93' : -0.63,
    '\xf0\x9f\xa4\x97' : 0.98,
    '\xf0\x9f\xa4\x94' : -0.15,
    '\xf0\x9f\xa4\xad' : -0.2,
    '\xf0\x9f\xa4\xab' : 0.01,
    '\xf0\x9f\xa4\xa5' : -0.07,
    '\xf0\x9f\x98\xb6' : -0.01,
    '\xf0\x9f\x98\x90' : -0.09,
    '\xf0\x9f\x98\x91' : -0.13,
    '\xf0\x9f\x98\xac' : -0.17,
    '\xf0\x9f\x99\x84' : 0.03,
    '\xf0\x9f\x98\xaf' : -0.02,
    '\xf0\x9f\x98\xa6' : -0.09,
    '\xf0\x9f\x98\xa7' : -0.14,
    '\xf0\x9f\x98\xae' : -0.06,
    '\xf0\x9f\x98\xb2' : 0.01,
    '\xf0\x9f\xa5\xb1' : -0.43,
    '\xf0\x9f\x98\xb4' : -0.56,
    '\xf0\x9f\xa4\xa4' : 0.86,
    '\xf0\x9f\x98\xaa' : -0.13,
    '\xf0\x9f\x98\xae\xe2\x80\x8d\xf0\x9f\x92\xa8' : 0.2,
    '\xf0\x9f\x98\xb5' : -0.7,
    '\xf0\x9f\x98\xb5\xe2\x80\x8d\xf0\x9f\x92\xab' : -0.57,
    '\xf0\x9f\xa4\x90' : -0.26,
    '\xf0\x9f\xa5\xb4' : -0.54,
    '\xf0\x9f\xa4\xa2' : -0.76,
    '\xf0\x9f\xa4\xae' : -0.88,
    '\xf0\x9f\xa4\xa7' : -0.1,
    '\xf0\x9f\x98\xb7' : -0.05,
    '\xf0\x9f\xa4\x92' : -0.1,
    '\xf0\x9f\xa4\x95' : -0.4,
    '\xf0\x9f\xa4\x91' : 0.5,
    '\xf0\x9f\xa4\xa0' : 0.4
}

















class NegRecommender():
    def __init__(self, num_users, num_items):
        self.matrix = csr_matrix((num_items, num_users), dtype=np.float32)
        self.negative_matrix = csr_matrix((num_items, num_users), dtype=np.float32)

        self.num_users = num_users
        self.num_items = num_items

        model_factors = round(min(num_items, num_users) ** 0.5)
        self.model = implicit.als.AlternatingLeastSquares(model_factors)#factors = model_factors)s
        self.negative_model = implicit.als.AlternatingLeastSquares(model_factors)
        #self.model = implicit.approximate_als.NMSLibAlternatingLeastSquares()

    def change_model_factors(self, new_factors):
        self.model = implicit.als.AlternatingLeastSquares(factors = new_factors)
        self.fit()

    def add_new_item(self):
        self.matrix._shape = (self.num_items + 1,self.num_users)
        self.matrix.indptr = np.hstack((self.matrix.indptr,self.matrix.indptr[-1]))        

        self.negative_matrix._shape = (self.num_items + 1,self.num_users)
        self.negative_matrix.indptr = np.hstack((self.negative_matrix.indptr,self.negative_matrix.indptr[-1]))        
        
        self.num_items += 1

        self.fit()

    def add_new_user(self):
        self.matrix = scipy.sparse.hstack((self.matrix,np.zeros(self.num_items,dtype=np.float32)[:,None]))
        self.negative_matrix = scipy.sparse.hstack((self.negative_matrix,np.zeros(self.num_items,dtype=np.float32)[:,None]))
        self.num_users += 1

        self.fit()

    def fit(self):
        self.model.fit(self.matrix)
        self.negative_model.fit(self.negative_matrix)

    def recommend(self, user_id, number_output):
        if user_id >= self.num_users:
            return None

        user_items = self.matrix.T.tocsr()
        neg_user_items = self.negative_matrix.T.tocsr()
        recommendations = self.model.recommend(user_id, user_items, N = self.num_items, filter_already_liked_items = True)
        anti_recommendations = self.negative_model.recommend(user_id, neg_user_items, N = self.num_items, filter_already_liked_items = True)

        recommendations.sort(key=lambda y: y[0])
        anti_recommendations.sort(key=lambda y: y[0])
        
        corrected_recommendations = []
        for i in range(len(recommendations)):
            corrected_recommendations.append((recommendations[i][0], recommendations[i][1] - anti_recommendations[i][1]))
        
        corrected_recommendations.sort(key=lambda y: y[1], reverse=True)
        corrected_recommendations = corrected_recommendations[:min(number_output, len(recommendations))]

        return corrected_recommendations

    def print_matrix(self):
        print(np.round(self.matrix.toarray() - self.negative_matrix.toarray(),2))
    
    def edit_matrix(self, user_list, item_list, score_list):
        assert(len(user_list) == len(item_list) and len(item_list) == len(score_list))

        lil_matrix = self.matrix.tolil()
        lil_negative_matrix = self.matrix.tolil()
        
        for i in range(len(user_list)):
            assert(item_list[i] < self.num_items and user_list[i] < self.num_users)
            if score_list[i] < 0:
                lil_negative_matrix[item_list[i], user_list[i]] = abs(score_list[i])
                lil_matrix[item_list[i], user_list[i]] = 10 ** (-20)
            elif score_list[i] > 0:
                lil_negative_matrix[item_list[i], user_list[i]] = 10 ** (-20)
                lil_matrix[item_list[i], user_list[i]] = score_list[i]
            else:
                lil_negative_matrix[item_list[i], user_list[i]] = 10 ** (-20)
                lil_matrix[item_list[i], user_list[i]] = 10 ** (-20)
            
        self.matrix = lil_matrix.tocsr()
        self.negative_matrix = lil_negative_matrix.tocsr()


class Recommender():
    def __init__(self, num_users, num_items):
        self.matrix = csr_matrix((num_items, num_users), dtype=np.float32)

        self.num_users = num_users
        self.num_items = num_items

        model_factors = 2#round(min(num_items, num_users) ** 0.5)
        self.model = implicit.als.AlternatingLeastSquares()#factors = model_factors)s
        #self.model = implicit.approximate_als.NMSLibAlternatingLeastSquares()

    def change_model_factors(self, new_factors):
        self.model = implicit.als.AlternatingLeastSquares(factors = new_factors)
        self.fit()

    def add_new_item(self):
        self.matrix._shape = (self.num_items + 1,self.num_users)

        self.matrix.indptr = np.hstack((self.matrix.indptr,self.matrix.indptr[-1]))        
        self.num_items += 1

        self.fit()

    def add_new_user(self):
        self.matrix = scipy.sparse.hstack((self.matrix,np.zeros(self.num_items,dtype=np.float32)[:,None]))
        self.num_users += 1

        self.fit()


    def fit(self):
        self.model.fit(self.matrix)

    def recommend(self, user_id, number_output):
        if user_id >= self.num_users:
            return None

        user_items = self.matrix.T.tocsr()
        recommendations = self.model.recommend(user_id, user_items, N = number_output, filter_already_liked_items = True)
        
        return recommendations

    def print_matrix(self):
        print(self.matrix.toarray())
    
    def edit_matrix(self, user_list, item_list, score_list):
        assert(len(user_list) == len(item_list) and len(item_list) == len(score_list))

        lil_matrix = self.matrix.tolil()
        
        for i in range(len(user_list)):
            assert(item_list[i] < self.num_items and user_list[i] < self.num_users)
            lil_matrix[item_list[i], user_list[i]] = score_list[i]

        self.matrix = lil_matrix.tocsr()

num_users = 5
num_items = 5

recommender = NegRecommender(num_users, num_items)

recommender.edit_matrix(
    [0,1,4,0,3,1,1,2,4,3,4,3,2,2,2,2,3,0,4],
    [0,1,2,2,4,0,1,2,3,4,0,1,2,3,4,1,4,4,3],
    [5,1,1,10,0.5,1,-1,1,1,1,1,-12,1,1,-1,-0.5,1,-1,-1])



for i in range(100):
    recommender.fit()

recommender.print_matrix()

recommendations = recommender.recommend(1, 10)

print(recommendations)
# for i in range(6):
#     print('User:' + str(i))d
#     recommendations = recommender.recommend(i, 1)

#     print(recommendations)