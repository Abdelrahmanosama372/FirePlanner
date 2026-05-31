(defun c:SETXDATA (/ app dtype val ss i ent edata xdatalist)

  ;; Ask for application name
  (setq app (getstring T "\nEnter Application Name: "))

  ;; Register app
  (regapp app)

  ;; Ask for data type
  (initget "String Integer Real")

  (setq dtype
    (getkword
      "\nData Type [String/Integer/Real] <String>: "
    )
  )

  ;; Default
  (if (null dtype)
    (setq dtype "String")
  )

  ;; Build XData
  (cond

    ;; STRING
    ((= dtype "String")
      (setq val (getstring T "\nEnter String Value: "))
      (setq xdatalist
        (list
          -3
          (list
            app
            (cons 1000 val)
          )
        )
      )
    )

    ;; INTEGER
    ((= dtype "Integer")
      (setq val (getint "\nEnter Integer Value: "))
      (setq xdatalist
        (list
          -3
          (list
            app
            (cons 1070 val)
          )
        )
      )
    )

    ;; REAL
    ((= dtype "Real")
      (setq val (getreal "\nEnter Real Value: "))
      (setq xdatalist
        (list
          -3
          (list
            app
            (cons 1040 val)
          )
        )
      )
    )
  )

  ;; Select objects
  (prompt "\nSelect objects: ")

  (if (setq ss (ssget))

    (progn

      (setq i 0)

      (while (< i (sslength ss))

        (setq ent (ssname ss i))

        ;; Get entity definition
        (setq edata (entget ent))

        ;; Append XData
        (entmod
          (append
            edata
            (list xdatalist)
          )
        )

        (setq i (1+ i))
      )

      (princ
        (strcat
          "\nXData added to "
          (itoa (sslength ss))
          " object(s)."
        )
      )
    )

    (princ "\nNo objects selected.")
  )

  (princ)
)