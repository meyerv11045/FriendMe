import implicit
import numpy as np
import scipy
from scipy.sparse import csr_matrix

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