class SnakeMatrix():
    def __init__(self,n):
        self.n = n
        self.matrix = self.matrix_initialization(self.n)
        if n%2:
            self.loop_num = n/2+1
        else:
            self.loop_num = n/2
        self.loop_order_list = range(self.loop_num)
        
    def matrix_initialization(self, n):
        size = range(n)
        matrix = [[] for i in size]
        for i in size:
            for i in size:
                matrix[i].append(0)
        return matrix
    
    def set_value(self,loop_order,start_value):
        loop_len = self.n-2*loop_order
        self.matrix[loop_order][loop_order]=start_value
        for j in range(loop_len):
            self.matrix[loop_order][loop_order+j]=start_value+j
        for i in range(loop_len):
            self.matrix[loop_order+i][self.n-loop_order-1]=self.matrix[loop_order][self.n-loop_order-1]+i
        for j in range(loop_len):
            self.matrix[self.n-loop_order-1][self.n-loop_order-1-j]=self.matrix[self.n-loop_order-1][self.n-loop_order-1]+j
        for i in range(loop_len-1):
            self.matrix[self.n-loop_order-1-i][loop_order]=self.matrix[self.n-loop_order-1][loop_order]+i
        return_value = self.matrix[loop_order+1][loop_order]+1
        return return_value
    
    def set_all_value(self):
        start_value = 1
        for i in self.loop_order_list:
            start_value = self.set_value(i,start_value)
        return self.matrix


if __name__ == "__main__":
    sm = SnakeMatrix(20)
    for i in sm.set_all_value():
        print i,"\n"
    
        
        
