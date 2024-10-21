class HomeworksWrap:
    @staticmethod
    def build(homeworks):
        res_dict = {}
        for homework in homeworks:
            if homework.subject_name in res_dict.keys():
                res_dict[homework.subject_name].append(homework)
            else:
                res_dict[homework.subject_name] = [homework]
        
        res_str = ""  
        for key, value in res_dict.items():
            res_str += f"\n🌟 <b>{key}:</b>\n"  
            for hw in value:
                status = "<b>Статус выполнения:</b> ✔️" if hw.is_done else "<b>Статус выполнения:</b> ❌"
                res_str += f"   • {hw.description} ({status})\n" 

        res_str += "\n✨ <b>Успехов в учебе!</b>"  
        return res_str.strip()
