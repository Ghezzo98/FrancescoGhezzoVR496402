(set-info :smt-lib-version 2.6)
(set-logic QF_UF)
(set-info :source |
Source: The calculus of computation (Bradley-Manna) 
Translator: |)
(set-info :category "crafted")
(set-info :status unsat)
(declare-sort S1 0)
(declare-fun f (S1) S1)
(declare-fun a () S1)
(assert (let ((t1 (f a)) (t2 (f t1 )) (t3 (f t2 )) (t4 (f t3 )) (t5 (f t4 ))) (and (= t3 a) (= t5 a) (not (= t1 a)) ) ))
(check-sat)
(exit)























