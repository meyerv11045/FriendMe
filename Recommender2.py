import implicit
import numpy as np
from numpy.lib.shape_base import column_stack
import scipy
from scipy.sparse import csr_matrix
from lightfm import LightFM


class Recommender():
    def __init__(self, num_users, num_items):
        self.matrix = csr_matrix((num_users, num_items), dtype=np.float32)

        self.num_users = num_users
        self.num_items = num_items

        model_factors = round(((num_items + num_users) / 2) ** 0.85)
        self.model = LightFM(loss='logistic', no_components = model_factors)

    def change_model_factors(self, new_factors):
        self.model = LightFM(loss='logistic', no_components = new_factors)
        self.fit(1000000)

    def add_new_item(self, num=1):
        self.matrix._shape = (self.num_users,self.num_items + num)
        self.matrix.indptr = np.hstack((self.matrix.indptr,self.matrix.indptr[-1]))

        self.num_items += num

    def add_new_user(self, num = 1):
        self.matrix._shape = (self.num_users + num,self.num_items)
        self.matrix.indptr = np.hstack((self.matrix.indptr,self.matrix.indptr[-1]))
        
        self.num_users += num

    def fit(self, num_times = 1):
        self.model.fit_partial(self.matrix, epochs = num_times, verbose=False)

    def reset_fit(self, num_times = 1):
        self.model.fit(self.matrix, epochs = num_times, verbose=False)

    def recommend(self, user_id, number_output):
        if user_id >= self.num_users:
            return None

        item_ids_with_rating = np.matrix(scipy.sparse.find(self.matrix[user_id, :])[1])
        user_items_test = np.setdiff1d(np.arange(0,self.num_items),item_ids_with_rating)
        
        if len(user_items_test) == 0:
            return None

        recommendations = np.array(self.model.predict(user_id, user_items_test))
        recommendations = np.column_stack((user_items_test,recommendations))
        #print(recommendations)
        sorted_recommendations = recommendations[np.flip(recommendations[:,1].argsort())]
        
        return sorted_recommendations[:number_output,:]

    def print_matrix(self):
        print(self.matrix.toarray())
    
    def edit_matrix(self, user_list, item_list, score_list):
        assert(len(user_list) == len(item_list) and len(item_list) == len(score_list))

        lil_matrix = self.matrix.tolil()
        
        for i in range(len(user_list)):
            assert(item_list[i] < self.num_items and user_list[i] < self.num_users)
            
            lil_matrix[user_list[i], item_list[i]] =score_list[i]
           
            
        self.matrix = lil_matrix.tocsr()


# num_users = 5
# num_items = 5

# recommender = Recommender(num_users, num_items)

# recommender.edit_matrix(
#     [0,1,4,0,3,1,1,2,4,3,4,3,2,2,2,2,3,0,4],
#     [0,1,2,2,4,0,1,2,3,4,0,1,2,3,4,1,4,4,3],
#     [5,1,1,10,0.5,1,-1,1,1,1,1,-12,1,1,-1,-0.5,1,-1,-1])


# recommender.fit(1000)

# recommender.print_matrix()

# recommendations = recommender.recommend(1, 1)



recommender2 = Recommender(5, 10)

recommender2.edit_matrix(
    [0,0,2,2,2,2,3,3,3,3,3,4,4,4,4,4,1,1],
    [0,1,0,1,2,3,2,3,4,5,6,4,5,6,7,8,7,8],
    [1,-1,1,-1,1,1,1,1,1,-1,-1,1,-1,-1,1,-1,1,-1])


recommender2.fit(1000)

recommender2.print_matrix()

recommendations = recommender2.recommend(1, 10)

print(recommendations)
