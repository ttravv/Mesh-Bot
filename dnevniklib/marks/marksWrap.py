class MarksWrap:
    @staticmethod
    def build(marks):
        res_dict = dict()
        for mark in marks:
            if mark.subject_name in res_dict.keys():
                res_dict[mark.subject_name].append(mark)
            else:
                res_dict[mark.subject_name] = [mark]
        
        res_str = ""
        for key, value in res_dict.items():
            res_str += f"\n📚 <b>{key}:</b> \n"  
            for mark in value:
                res_str += f"<b>⭐ {str(mark)}\n</b>"  

        return res_str
