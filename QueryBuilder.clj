(ns querybuilderclojure.clojure.core
  (:gen-class))

(require 'clojure.string)

(defn chain
  ([strings]
   (reduce (fn [current bonus] 
             (str (name current) ", " (name bonus))) strings))
  ([strings joiner] 
   (reduce (fn [current bonus] 
             (str (name current) joiner (name bonus))) strings)))

(defn convertOrderBy [s]
  (case (.substring s 0 1)
    "!" (str (.substring s 1 (.length s)) " DESC")
    (str s " ASC")))

(defn chainOrderBy
  ([strings]
   (reduce (fn [current bonus] 
             (str 
               (if (.contains (name current) " ") 
                 (name current)
                 (convertOrderBy (name current)))
               ", " (convertOrderBy (name bonus))))
           strings)))


(defn SELECT
  ;; No arguments
  ([]
   (SELECT "*"))
  ;; Multiple arguments
  ([& args]
   (str "SELECT " 
     (chain args))))

(defn INSERT_INTO [table & args]
  (str "INSERT INTO " table " ("
    (chain args) ")"))

(defn VALUES [qry & args]
  (str qry " VALUES (" 
    (chain args) ")"))

(defn SET [qry & args]
  (str qry " SET " 
    (chain args)))

(defn UPDATE [table]
  (str "UPDATE " table))

(defn DELETE_FROM [table]
  (str "DELETE FROM " table))

(defn FROM [qry table]
  (str qry " FROM " table))

(defn parenthesis [string]
  (str "(" (name string) ")"))

(defn OR [& parts]
  (-> (chain parts " OR ") parenthesis))

(defn AND [& parts]
  (-> (chain parts " AND ") parenthesis))

(defn WHERE
  ;; No additional arguments
  ([qry]
   (qry))
  ([qry args]
   (str qry " WHERE "  args)))

(defn ON [on]
  (str " ON " on))

(defn ORDER_BY
  ([qry]
   (qry))
  ([qry & args]
   (str qry " ORDER BY " 
     (chainOrderBy args))))

(defn COMPARATOR [a sign b]
  (str (name a) " " sign " " (name b)))

(defn LIMIT
  ([qry num]
   (str qry " LIMIT " num))
  ([qry num offset]
   (str qry " LIMIT " num ", " offset)))

(defn EQUAL [a b]
  (COMPARATOR a "==" b))

(defn NOT_EQUAL [a b]
  (COMPARATOR a "!=" b))

(defn GREATER [a b]
  (COMPARATOR a ">" b))

(defn GREATER_OR_EQUAL [a b]
  (COMPARATOR a ">=" b))

(defn LESSER [a b]
  (COMPARATOR a "<" b))

(defn LESSER_OR_EQUAL [a b]
  (COMPARATOR a "<=" b))

(defn LIKE [a b]
  (COMPARATOR a "LIKE" b))  

(defn JOIN 
  ([qry joinType table]
   (str qry " " (-> (name joinType) clojure.string/upper-case)" JOIN " table))
  ([qry joinType table on]
   (str (JOIN qry joinType table) on)))
                              

(defn -main []
  (println "\nSELECT TEST QUERY: \n")
  (println (->
              (SELECT :u.id :v.id :u.username :v.username)
              (FROM "User u")
              (JOIN :left "User v" 
                (ON
                (OR
                  (EQUAL :u.username :v.username)
                  (EQUAL :u.email :v.email))))
              (WHERE 
                (NOT_EQUAL :u.id :v.id))
              (ORDER_BY :!u.id  :u.username)
              (LIMIT 2)))
              
  (println "\nINSERT TEST QUERY: \n")
  (println (->
              (INSERT_INTO "User" :username :email)
              (VALUES "igor93" "igorsamurovic@hotmail.com")))         

  (println "\nUPDATE TEST QUERY: \n")
  (println (->
              (UPDATE "User")
              (SET "username=Igor93" "email=igorsamurovic@gmail.com")
              (WHERE 
                (EQUAL :id :1))))

  (println "\nDELETE TEST QUERY: \n")
  (println (->
              (DELETE_FROM "User")
              (WHERE 
                (EQUAL :id :1))))
              

)

