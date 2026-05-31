(defun c:RESETXDATA (/ app ss i ent vla-obj xtype xdata)
  (vl-load-com)

  ;; Get the app name (e.g., FP)
  (setq app (getstring T "\nEnter Application Name to remove: "))

  (if (/= app "")
    (progn
      ;; Still register it just to be safe
      (regapp app)
      
      (prompt "\nSelect objects to strip XData from: ")
      (if (setq ss (ssget))
        (progn
          ;; Prepare the variant arrays that ActiveX expects for clearing XData
          ;; DXF 1001 indicates the Application Name
          (setq xtype (vlax-make-safearray vlax-vbInteger '(0 . 0)))
          (vlax-safearray-put-element xtype 0 1001)
          
          ;; The string value of the application name itself
          (setq xdata (vlax-make-safearray vlax-vbVariant '(0 . 0)))
          (vlax-safearray-put-element xdata 0 app)

          (setq i 0)
          (while (< i (sslength ss))
            (setq ent (ssname ss i))
            
            ;; Convert the traditional entity name to a VLA-Object
            (setq vla-obj (vlax-ename->vla-object ent))
            
            ;; Set the XData using our empty structures.
            ;; This purges the app's data completely without entmod errors.
            (vla-SetXData vla-obj xtype xdata)
            
            (setq i (1+ i))
          )
          (princ (strcat "\nSuccessfully purged XData for application: \"" app "\" via ActiveX."))
        )
        (princ "\nNo objects selected.")
      )
    )
    (princ "\nInvalid application name.")
  )
  (princ)
)